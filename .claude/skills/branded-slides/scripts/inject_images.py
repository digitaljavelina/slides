#!/usr/bin/env python3
"""
inject_images.py — branded-slides image orchestrator.

Parses an HTML deck, determines per-slide image role, builds prompts via
the brand suffix matching the deck's palette mode, calls OpenRouter
Nano Banana 2 to generate images, caches them under <deck>/images/, and
idempotently injects <img class="slide-bg"> or <aside class="slide-image">
elements into the deck.

Stdlib only (urllib for HTTP, html.parser for content extraction, re for
section-level rewrites). No external dependencies.

Usage:
  inject_images.py <deck.html>                 # full pass: gen + inject
  inject_images.py <deck.html> --dry-run       # show plan, don't call API
  inject_images.py <deck.html> --inject-only   # use existing cache, no API
  inject_images.py <deck.html> --refresh       # ignore all caches
  inject_images.py <deck.html> --refresh-slide <id>
  inject_images.py <deck.html> --limit N       # generate at most N images
  inject_images.py <deck.html> --hero-2k       # use 2K size for title slide

Env:
  OPENROUTER_API_KEY     (required for non-dry-run)
"""

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

# ============================================================
# Brand suffixes — verbatim, do not edit casually. Editing
# invalidates every prompt-hash on next run (forces full regen).
# Mirror these in docs/IMAGE_PROMPT_GUIDE.md if changed.
# ============================================================
BRAND_SUFFIXES = {
    ("light-clinical", "background"): (
        "Editorial illustration suitable as a slide background. "
        "Solid off-white background (#fafafa), single deep-blue accent (#2563eb). "
        "Minimal, photographic or illustrated line-art. "
        "Anatomical or scientific subjects rendered as clean monochrome line-art "
        "with selective blue accent fills. No text. No watermarks. 16:9 aspect."
    ),
    ("light-clinical", "contextual"): (
        "Editorial illustration for the right side of a slide. "
        "White or off-white background, single deep-blue accent (#2563eb). "
        "Subject centered with breathing room around it. "
        "Anatomical line-art, scientific diagram, or photographic histology. "
        "No text overlays. Composition with empty negative space on the left "
        "(text will overlay there). 4:5 aspect."
    ),
    ("dark-minimal", "background"): (
        "Cinematic editorial photograph or illustration suitable as a slide background. "
        "Near-black background (#0a0a0a), single vivid red accent (#ef4444) used sparingly. "
        "Moody, low-key lighting. Scientific subject (anatomy, cell, instrument, abstract data shape) "
        "rendered photographically or as silhouette. No text. No watermarks. 16:9 aspect."
    ),
    ("dark-minimal", "contextual"): (
        "Cinematic editorial illustration for the right side of a slide. "
        "Dark near-black background, single vivid red accent (#ef4444). "
        "Subject offset to the right of frame; left half is empty dark negative space "
        "(text will overlay there). Photographic or stylized; no text. 4:5 aspect."
    ),
}

# OpenRouter model chain. Pinned per reference_openrouter_nano_banana memory.
PRIMARY_MODEL = "google/gemini-3.1-flash-image-preview"
FALLBACK_MODEL = "google/gemini-2.5-flash-image"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Where to look for the API key, in priority order.
# Both var names supported (the user's existing setup uses OPENROUTER_KEY).
API_KEY_ENV_NAMES = ("OPENROUTER_API_KEY", "OPENROUTER_KEY")
# If neither env var is set, fall back to reading these dotenv-style files.
API_KEY_FILE_FALLBACKS = (Path.home() / ".claude" / ".env",)


def resolve_api_key() -> str:
    """Resolve the OpenRouter key from env vars, then from dotenv-style fallback files."""
    for name in API_KEY_ENV_NAMES:
        val = os.environ.get(name, "").strip()
        if val:
            return val
    # Dotenv fallback. Tiny ad-hoc parser — stdlib only, no dotenv lib.
    for path in API_KEY_FILE_FALLBACKS:
        if not path.is_file():
            continue
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() in API_KEY_ENV_NAMES:
                    return v.strip().strip("'\"")
        except OSError:
            continue
    return ""

# Approximate cost estimates (cents). Used for the summary at end of run;
# actual billing is via output tokens, so these are rough.
COST_CENTS = {"1K": 5, "2K": 12, "4K": 30}


# ============================================================
# HTML parsing
# ============================================================

SLIDE_RE = re.compile(
    r'(<section\b[^>]*\bclass="[^"]*\bslide\b[^"]*"[^>]*>)(.*?)(</section>)',
    re.DOTALL,
)
ATTR_RE = re.compile(r'(\w[\w-]*)="([^"]*)"')
PALETTE_RE = re.compile(r'<body\b[^>]*\bdata-palette="([^"]+)"', re.IGNORECASE)


class TextExtractor(HTMLParser):
    """Pull plain text from a small HTML fragment, plus track when we're
    inside an `.eyebrow` or an `<h1>`/`<h2>`. Used per-slide."""

    def __init__(self):
        super().__init__()
        self.depth_eyebrow = 0
        self.depth_h1 = 0
        self.depth_h2 = 0
        self.eyebrow_buf = []
        self.h1_buf = []
        self.h2_buf = []
        self.element_count = 0

    def handle_starttag(self, tag, attrs):
        attr_d = dict(attrs)
        # HTMLParser yields None for valueless attributes (e.g. `disabled`).
        # Coerce to "" so .split() is safe.
        klass = attr_d.get("class") or ""
        kclasses = klass.split()
        if "eyebrow" in kclasses:
            self.depth_eyebrow += 1
        if tag == "h1":
            self.depth_h1 += 1
        if tag == "h2":
            self.depth_h2 += 1
        # Element count for role heuristic: count cards / rows / timeline items.
        if any(c in kclasses for c in ("card", "row", "t-item")):
            self.element_count += 1

    def handle_endtag(self, tag):
        if tag == "h1":
            self.depth_h1 = max(0, self.depth_h1 - 1)
        if tag == "h2":
            self.depth_h2 = max(0, self.depth_h2 - 1)
        # Eyebrow ends when its containing tag closes; we approximate by
        # closing on any tag close while inside it (good enough for a single
        # eyebrow span on each slide).
        if self.depth_eyebrow > 0 and tag in ("span", "div", "p"):
            self.depth_eyebrow -= 1

    def handle_data(self, data):
        if self.depth_eyebrow > 0:
            self.eyebrow_buf.append(data)
        if self.depth_h1 > 0:
            self.h1_buf.append(data)
        if self.depth_h2 > 0:
            self.h2_buf.append(data)


def slug(value: str, fallback: str) -> str:
    """Slugify a data-title for use as a filesystem ID."""
    s = re.sub(r"[^a-zA-Z0-9]+", "-", value or "").strip("-").lower()
    return s or fallback


def parse_section_attrs(open_tag: str) -> dict:
    return {m.group(1): m.group(2) for m in ATTR_RE.finditer(open_tag)}


def extract_slide_meta(open_tag: str, inner: str, idx: int) -> dict:
    """Pull the metadata we need from one slide's HTML."""
    attrs = parse_section_attrs(open_tag)
    title = attrs.get("data-title", "")
    slide_id = slug(title, f"slide-{idx + 1}")
    if "data-image-id" in attrs:
        slide_id = attrs["data-image-id"]

    extractor = TextExtractor()
    extractor.feed(inner)
    eyebrow = " ".join(extractor.eyebrow_buf).strip()
    h1 = " ".join(extractor.h1_buf).strip()
    h2 = " ".join(extractor.h2_buf).strip()
    headline = h2 or h1

    # ATTR_RE only captures key="value" attrs; valueless ones (e.g. `data-no-image`)
    # are detected by string-search on the opening tag itself.
    no_image = bool(re.search(r"\bdata-no-image\b", open_tag))
    role_override = attrs.get("data-image-role")
    prompt_override = attrs.get("data-image-prompt")
    prompt_raw = attrs.get("data-image-prompt-raw")

    return {
        "id": slide_id,
        "index": idx,
        "title": title,
        "eyebrow": eyebrow,
        "headline": headline,
        "is_title_slide": "title-slide" in attrs.get("class", "").split(),
        "no_image": no_image,
        "role_override": role_override,
        "prompt_override": prompt_override,
        "prompt_raw": prompt_raw,
        "element_count": extractor.element_count,
        "has_bg_image": 'class="slide-bg"' in inner or "class='slide-bg'" in inner,
        "has_side_image": 'class="slide-image"' in inner or "class='slide-image'" in inner,
    }


def determine_role(meta: dict) -> str:
    """Pick image role per slide. Honors data-no-image and data-image-role."""
    if meta["no_image"]:
        return "none"
    if meta["role_override"] in ("background", "contextual", "none"):
        return meta["role_override"]
    n = meta["element_count"]
    if n <= 2:
        return "background"
    if n <= 6:
        return "contextual"
    return "none"


def build_prompt(meta: dict, role: str, palette: str) -> str:
    """Assemble the final prompt sent to the API."""
    if meta["prompt_raw"]:
        return meta["prompt_raw"]  # full override, no brand suffix
    suffix = BRAND_SUFFIXES.get((palette, role), "")
    if meta["prompt_override"]:
        return f"{meta['prompt_override']}. {suffix}".strip()
    parts = [p for p in (meta["eyebrow"], meta["headline"]) if p]
    base = ". ".join(parts) if parts else meta["title"] or "Abstract scientific subject"
    return f"{base}. {suffix}".strip()


# ============================================================
# Cache
# ============================================================


def prompt_hash(prompt: str, model: str, image_size: str) -> str:
    h = hashlib.sha256()
    h.update(prompt.encode("utf-8"))
    h.update(b"|")
    h.update(model.encode("utf-8"))
    h.update(b"|")
    h.update(image_size.encode("utf-8"))
    return h.hexdigest()


def cache_paths(images_dir: Path, slide_id: str) -> tuple[Path, Path]:
    return (
        images_dir / f"{slide_id}.png",
        images_dir / f".{slide_id}.prompt",
    )


def cache_hit(images_dir: Path, slide_id: str, expected_hash: str) -> bool:
    img, sidecar = cache_paths(images_dir, slide_id)
    if not img.exists() or not sidecar.exists():
        return False
    try:
        return sidecar.read_text(encoding="utf-8").strip() == expected_hash
    except OSError:
        return False


# ============================================================
# OpenRouter API
# ============================================================


def call_openrouter(prompt: str, model: str, image_size: str, api_key: str, timeout: int = 90) -> bytes:
    """Make one image-generation request. Returns raw PNG bytes.
    Raises urllib.error.HTTPError or RuntimeError on failure."""
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["image", "text"],
            "image_config": {"aspect_ratio": "16:9", "image_size": image_size},
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        ENDPOINT,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=body,
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    try:
        images = payload["choices"][0]["message"].get("images") or []
        if not images:
            raise RuntimeError("API response contained no images")
        data_url = images[0]["image_url"]["url"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected API response shape: {exc}") from exc

    if "," not in data_url:
        raise RuntimeError("Image data URL missing comma separator")
    return base64.b64decode(data_url.split(",", 1)[1])


def generate_with_fallback(prompt: str, image_size: str, api_key: str) -> tuple[bytes, str]:
    """Try primary then fallback model. Returns (bytes, model_used)."""
    try:
        return call_openrouter(prompt, PRIMARY_MODEL, image_size, api_key), PRIMARY_MODEL
    except urllib.error.HTTPError as exc:
        if exc.code >= 500:
            return call_openrouter(prompt, FALLBACK_MODEL, image_size, api_key), FALLBACK_MODEL
        raise


# ============================================================
# HTML rewrite (idempotent)
# ============================================================


def inject_into_slide(inner: str, role: str, image_path: str) -> str:
    """Return new inner HTML with the image element added (or unchanged
    if already present). Idempotent: re-running with the same role/path
    is a no-op."""
    if role == "background":
        if 'class="slide-bg"' in inner:
            return inner  # already injected
        bg_tag = f'\n      <img class="slide-bg" src="{image_path}" alt="" aria-hidden="true">\n'
        return bg_tag + inner

    if role == "contextual":
        if 'class="slide-image"' in inner:
            return inner
        aside = (
            f'\n        <aside class="slide-image"><img src="{image_path}" alt="" aria-hidden="true"></aside>\n'
        )
        # Insert before the closing </div> of the LAST slide-content (handles nested correctly).
        idx = inner.rfind("</div>")
        if idx == -1:
            return inner  # malformed slide; skip silently
        return inner[:idx] + aside + inner[idx:]

    return inner


# ============================================================
# Main
# ============================================================


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("deck", type=Path, help="Path to deck HTML file")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--inject-only", action="store_true",
                    help="Skip API calls; only inject from existing cache")
    ap.add_argument("--refresh", action="store_true",
                    help="Ignore all prompt-hash caches; regenerate everything")
    ap.add_argument("--refresh-slide", action="append", default=[],
                    help="Regenerate this slide-id (can be passed multiple times)")
    ap.add_argument("--limit", type=int, default=None,
                    help="Process at most N slides this run (useful for testing)")
    ap.add_argument("--hero-2k", action="store_true",
                    help="Use image_size=2K for the title slide")
    args = ap.parse_args()

    deck_path: Path = args.deck.resolve()
    if not deck_path.is_file():
        print(f"ERROR: deck not found: {deck_path}", file=sys.stderr)
        return 1

    deck_dir = deck_path.parent
    images_dir = deck_dir / "images"
    images_dir.mkdir(exist_ok=True)
    error_log = images_dir / ".errors.log"

    html_text = deck_path.read_text(encoding="utf-8")

    palette_match = PALETTE_RE.search(html_text)
    palette = palette_match.group(1) if palette_match else "dark-minimal"
    if palette not in ("light-clinical", "dark-minimal"):
        print(f"WARN: unknown palette '{palette}', defaulting to dark-minimal", file=sys.stderr)
        palette = "dark-minimal"

    matches = list(SLIDE_RE.finditer(html_text))
    if not matches:
        print("ERROR: no <section class=\"slide\"> elements found in deck", file=sys.stderr)
        return 1

    api_key = resolve_api_key()
    if not args.dry_run and not args.inject_only and not api_key:
        print(
            "ERROR: no OpenRouter API key found.\n"
            "  Looked at env vars: OPENROUTER_API_KEY, OPENROUTER_KEY\n"
            "  Looked at files:    ~/.claude/.env\n"
            "Set one with:\n"
            "  export OPENROUTER_KEY='your-key-here'  # or add to ~/.zshrc\n"
            "Get a key at https://openrouter.ai/keys.",
            file=sys.stderr,
        )
        return 2

    # ---- Plan phase ----
    plan = []
    for idx, m in enumerate(matches):
        meta = extract_slide_meta(m.group(1), m.group(2), idx)
        role = determine_role(meta)
        if role == "none":
            plan.append({**meta, "role": role, "prompt": None, "size": None})
            continue
        prompt = build_prompt(meta, role, palette)
        size = "2K" if (args.hero_2k and meta["is_title_slide"]) else "1K"
        plan.append({**meta, "role": role, "prompt": prompt, "size": size})

    # ---- Dry-run output ----
    if args.dry_run:
        print(f"Deck: {deck_path}")
        print(f"Palette: {palette}")
        print(f"{len(matches)} slides total\n")
        for s in plan:
            mark = "·" if s["role"] != "none" else " "
            print(f"  {mark} [{s['id']}] role={s['role']:11} elements={s['element_count']}")
            if s["prompt"]:
                snippet = s["prompt"][:120] + ("…" if len(s["prompt"]) > 120 else "")
                print(f"      prompt: {snippet}")
        billable = [s for s in plan if s["role"] != "none"]
        est = sum(COST_CENTS.get(s["size"], 0) for s in billable)
        print(f"\n{len(billable)} billable slides; estimated ~${est / 100:.2f} on first run.")
        return 0

    # ---- Generation phase ----
    api_calls = 0
    cache_hits = 0
    soft_failures = 0
    total_cents = 0

    refresh_set = set(args.refresh_slide)

    for s in plan:
        if s["role"] == "none":
            continue
        if args.limit is not None and api_calls >= args.limit:
            break

        slide_id = s["id"]
        size = s["size"]
        prompt = s["prompt"]
        h = prompt_hash(prompt, PRIMARY_MODEL, size)

        force = args.refresh or slide_id in refresh_set
        if not force and cache_hit(images_dir, slide_id, h):
            cache_hits += 1
            continue

        if args.inject_only:
            # No API calls allowed; skip cache misses silently.
            continue

        print(f"  [{slide_id}] generating {size} via {PRIMARY_MODEL}...", flush=True)
        try:
            png_bytes, _model_used = generate_with_fallback(prompt, size, api_key)
        except Exception as exc:  # noqa: BLE001 — broad on purpose; soft-fail per D-10
            soft_failures += 1
            with error_log.open("a", encoding="utf-8") as f:
                f.write(f"[{slide_id}] {type(exc).__name__}: {exc}\n")
            print(f"  [{slide_id}] FAILED ({type(exc).__name__}); see {error_log}", file=sys.stderr)
            continue

        img_path, sidecar_path = cache_paths(images_dir, slide_id)
        img_path.write_bytes(png_bytes)
        sidecar_path.write_text(h, encoding="utf-8")
        api_calls += 1
        total_cents += COST_CENTS.get(size, 0)

    # ---- Inject phase (always run, idempotent) ----
    new_html = []
    cursor = 0
    injected = 0
    for s, m in zip(plan, matches):
        new_html.append(html_text[cursor:m.start()])
        open_tag, inner, close_tag = m.group(1), m.group(2), m.group(3)

        img_path, _ = cache_paths(images_dir, s["id"])
        if s["role"] in ("background", "contextual") and img_path.exists():
            rel_img = f"images/{s['id']}.png"
            new_inner = inject_into_slide(inner, s["role"], rel_img)
            if new_inner != inner:
                injected += 1
            inner = new_inner

        new_html.append(open_tag)
        new_html.append(inner)
        new_html.append(close_tag)
        cursor = m.end()
    new_html.append(html_text[cursor:])
    deck_path.write_text("".join(new_html), encoding="utf-8")

    # ---- Summary ----
    print()
    print(f"Deck: {deck_path}")
    print(f"Slides: {len(plan)}    Billable: {sum(1 for s in plan if s['role'] != 'none')}")
    print(f"API calls: {api_calls}    Cache hits: {cache_hits}    Soft failures: {soft_failures}")
    print(f"Injected this run: {injected}")
    if api_calls:
        print(f"Estimated cost: ~${total_cents / 100:.2f}  (rough — confirmed via OpenRouter dashboard)")
    if soft_failures:
        print(f"See {error_log} for details on failed slides.")
    return 0 if soft_failures == 0 else 0  # soft-fail policy: never exit non-zero on image errors


if __name__ == "__main__":
    sys.exit(main())
