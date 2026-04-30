---
name: branded-slides
description: Author beautiful HTML decks with the project's locked brand (Space Grotesk + Inter, 16-px-min body, no italic emphasis, minimal chrome) plus optional AI image generation via OpenRouter Nano Banana 2. Use when the user asks for a deck, slides, talk, or presentation in this repo and wants the iterated visual style applied automatically. For editable PowerPoint output, cross-reference the in-repo `marp-slides` skill instead.
---

# branded-slides

A project-scoped skill that produces a single self-contained HTML deck with the brand the user iterated to over six redirects on the AI-in-Safety-Pharmacology deck. The brand is **locked** — palette mode is the only style decision per deck.

Optional second pass: AI-generated images per slide via OpenRouter Nano Banana 2 (`google/gemini-3.1-flash-image-preview`). Image generation is deliberate and batch-mode — never auto-runs on every build.

## When to use this skill

Trigger on any of:

- "Make me a deck about X"
- "Build a presentation on X"
- "Turn this paper into slides"
- "Slides for a talk on X"
- Any request involving slides/decks/presentations in this repo

If the user explicitly asks for **editable PowerPoint output** (".pptx I can edit in Keynote/PowerPoint"), use the in-repo `marp-slides` skill instead — it owns that path. See `docs/PPTX_EXPORT.md` for a hand-off note.

## How it works

```
Source paper / outline / topic
        │
        ▼
Phase 1  ─►  Discover content + palette mode (Light Clinical | Dark Minimal)
        │
        ▼
Phase 2  ─►  Generate brand-locked HTML deck from templates/template.html
        │
        ▼
Phase 3  ─►  (optional) generate_images.sh → AI images per slide via OpenRouter
        │
        ▼
Phase 4  ─►  Open in browser, report cost summary, hand off
```

The brand `<style>` block is shipped verbatim from `templates/template.html` (which is the user's accepted artefact captured byte-for-byte). Do not re-derive it from scratch.

## Phase 0 — Detect mode

- **Mode A: New deck** (most common) — content from a paper, an outline, or a topic. Go to Phase 1.
- **Mode B: Re-skin existing deck** — user provides an existing `.html` and wants it rebranded. Read its `<style>` block, replace with the contents of `templates/template.html`'s `<style>` block, preserve content. Skip Phase 1 question 1 (content); ask only question 2 (palette).
- **Mode C: Add images to existing deck** — user provides a deck path. Skip Phase 1 entirely; jump to Phase 3.

## Phase 1 — Content + palette discovery

Use **one** `AskUserQuestion` call with at most three questions:

1. **Content source** (`header: "Content"`):
   - "I'll provide an outline" — user pastes content
   - "Use a paper from my Obsidian `learning/` folder" — Claude reads it (the path lives in the project memory; check there for the exact location)
   - "Topic only — Claude drafts" — Claude generates the 10-slide arc itself

2. **Palette mode** (`header: "Palette"`):
   - "Light Clinical (Recommended)" — `#fafafa` background, `#2563eb` blue accent, near-black text
   - "Dark Minimal" — `#0a0a0a` background, `#ef4444` red accent, white text

3. **Image generation** (`header: "Images"`):
   - "Generate after I review the content (Recommended)" — produce text-only deck first; user reviews; then run `generate_images.sh`
   - "Skip — text-only deck" — no images at all

Do NOT offer style presets. The brand is locked. The 12 frontend-slides presets are deliberately not included; this skill is brand-locked.

## Phase 2 — Generate the deck

1. Choose an output location: `decks/<slug>/` (create if missing). The deck file is `index.html`.
2. Read `templates/template.html`. It contains the full `<style>` block (verbatim brand) plus placeholders:
   - `<!-- DATA-PALETTE -->` — replace with `light-clinical` or `dark-minimal` on the `<body data-palette="...">`
   - `<!-- SLIDES -->` — replace with the actual `<section class="slide">` elements
3. Compose slides using patterns from `templates/slide-patterns.md`. The 10-slide arc mirrors the source paper's own structure (e.g., its graphical abstract). Default arc when no paper is given:
   1. Title (sparse → ideal for hero image later)
   2. The problem (3 cards or rows)
   3. Foundations / context (3 cards)
   4. Application 1 (3-up cards)
   5. Application 2 (row-list of 4)
   6. Application 3 (pull-quote + 3 cards)
   7. Data / numbers (ring or stat row)
   8. Regulatory / timeline (vertical timeline)
   9. Challenges / limits (4-up grid)
   10. Future / closing (3 cards + pull-quote)
4. Add `data-image-prompt="..."` to slides that should receive an AI image (Phase 3 will read these). Skip the attribute on slides that should never get an image.
5. Write the composed HTML to `decks/<slug>/index.html`.
6. Open it: `open decks/<slug>/index.html`.

**Brand rules to honor while authoring** (these come from `BRAND.md`; stay consistent):

- Body weight is `400` (not 300). Inter at 300 reads gauzy on backgrounds.
- `<em>` is solid accent + weight 600 — **not** italic. Sans italics don't carry the editorial flourish that emphasis needs.
- Body-size minimum at desktop max ≈ 16px. Use the existing `var(--body-size)` token; never hardcode `clamp(...)` triplets in component rules — that creates drift the user will catch.
- No corner badges, slide-number indicators, keyboard-hint footers, or background orbs/grain. Right-edge nav dots + top progress bar already communicate slide position.
- Inline SVG over CDN images. Decorative strokes use `stroke="currentColor"` so a parent `color: var(--accent)` retints them on theme swap.

## Phase 3 — Optional: image generation

Only if the user opted in during Phase 1, **or** they ask later "now generate the images." Image generation is a separate batch pass invoked by the user — never auto-on-every-build, because Nano Banana 2 calls cost money even with credits.

```bash
scripts/generate_images.sh decks/<slug>/index.html
```

Behind the scenes the script:

1. Parses each `<section class="slide">` for content density (counts `.card`, `.row`, headings) → picks an image **role**:
   - ≤2 content elements → **background** (full-bleed `<img class="slide-bg">` with palette-aware overlay)
   - 3–6 elements → **contextual** (`<aside class="slide-image">` taking ~40% width)
   - ≥7 elements OR `data-no-image` attr → **none** (skip)
2. Builds the prompt from `data-image-prompt` (override) OR auto-derived from `eyebrow + h2 + brand suffix` (see `docs/IMAGE_PROMPT_GUIDE.md`).
3. Calls OpenRouter with `google/gemini-3.1-flash-image-preview`; on 5xx falls back to `google/gemini-2.5-flash-image`.
4. Caches images at `decks/<slug>/images/<slide-id>.png` keyed by prompt-hash sidecar `decks/<slug>/images/.<slide-id>.prompt`. Re-runs reuse the cache; only changed prompts regenerate.
5. Invokes `scripts/inject_images.py` to idempotently rewrite the deck HTML with the image elements.
6. Prints a cost summary at the end.

`OPENROUTER_API_KEY` must be set. If missing, the script prints setup instructions and exits with no API calls.

## Phase 4 — Deliver

Open the deck and report:

> Built `decks/<slug>/index.html` ({palette-mode}, 10 slides).
> {if images: Added N AI images at `decks/<slug>/images/`, ~$X.XX cost summary.}
> Edit content directly in the HTML file. To regenerate images for a slide, edit its `data-image-prompt` and re-run `generate_images.sh`.
> For editable PowerPoint, see `.claude/skills/branded-slides/docs/PPTX_EXPORT.md`.

## File map

```
.claude/skills/branded-slides/
├── SKILL.md                      # this file
├── BRAND.md                      # locked :root CSS, durable visual rules, alias pattern
├── templates/
│   ├── template.html             # brand-locked HTML shell with placeholders
│   ├── slide-patterns.md         # HTML snippets for each layout pattern
│   └── starter-deck.html         # 10-slide example deck pre-filled with brand
├── scripts/
│   ├── generate_images.sh        # OpenRouter image-gen orchestrator
│   └── inject_images.py          # idempotent HTML rewriter (stdlib only)
├── assets/
│   └── icons/                    # inline-SVG icons (currentColor strokes)
└── docs/
    ├── PPTX_EXPORT.md            # cross-reference to marp-slides for editable PPTX
    └── IMAGE_PROMPT_GUIDE.md     # auto-prompt construction + brand suffixes
```

## Tooling requirements

- **Bash + curl** — Phase 3 image generation
- **python3 (stdlib only)** — `inject_images.py`. No `pillow`, no `python-pptx`.
- **A modern browser** — Phase 4 preview. Decks are scroll-snap HTML.
- **OpenRouter API key** — only required for Phase 3. The skill auto-resolves it from (in order): `$OPENROUTER_API_KEY`, `$OPENROUTER_KEY`, then dotenv-style file `~/.claude/.env` (which Claude Code already maintains for many users). No need to copy keys around — set it in any one of those places.

No Node/npm. No package install during normal use. The deck is a single `index.html` file plus an `images/` folder.

## Cross-references

- **Editable PowerPoint output** — `.claude/skills/marp-slides/SKILL.md` (in this repo). The two skills coexist; pick by output format.
- **Brand guidelines source of truth** — `BRAND.md` in this skill.
- **OpenRouter API shape** — see the user's reference memory at `~/.claude/projects/-Users-michaelhenry-Documents-Projects-claude-slides/memory/reference_openrouter_nano_banana.md`.

## Validation checklist before reporting "done"

- [ ] Deck file exists at `decks/<slug>/index.html` and has non-zero size.
- [ ] `<body data-palette="...">` matches the user's chosen palette.
- [ ] Every slide has exactly one `<h2>` (or `<h1>` on the title slide); no `<h1>` on non-title slides.
- [ ] No slide contains a wall of prose. If a slide reads like a paragraph, split or trim.
- [ ] If images were generated: `images/` folder exists, every cached PNG has a sibling `.prompt` sidecar, and the deck HTML references the images.
- [ ] Open the deck in a browser; confirm scroll-snap works, nav dots highlight the active slide, and there are no console errors.
