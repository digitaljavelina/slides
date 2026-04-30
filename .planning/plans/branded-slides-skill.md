---
slug: branded-slides-skill
created: 2026-04-29
status: active
type: feature
summary: New project-scoped Claude Code skill at .claude/skills/branded-slides/ that generates HTML decks with the iterated dark/red and light/blue brand baked in, an editable-PPTX fallback path via the existing marp-slides skill, and AI image generation via OpenRouter's Nano Banana 2 (google/gemini-3.1-flash-image-preview).
decisions:
  - id: D-01
    choice: Skill name = `branded-slides`; lives at `.claude/skills/branded-slides/` in this repo
    rationale: Stated location ("lives at .claude/skills/<new-skill-name>/"). Name reflects "brand baked in" without being narrowly pharma-specific so it can serve future scientific decks too. The user's own working-name suggestion was "branded-slides or pharma-slides"; pick the more general one.
  - id: D-02
    choice: Primary output format = single self-contained HTML; PPTX = opt-in via cross-reference to existing marp-slides skill (no duplication)
    rationale: Image-generation flow is HTML-native (background images, contextual images, scroll-snap reveals over hero imagery). Marp-slides already owns editable-PPTX via pandoc; duplicating that path is wasted work. Cross-reference keeps both skills clean and avoids regressions.
  - id: D-03
    choice: OpenRouter model slug = `google/gemini-3.1-flash-image-preview` (Nano Banana 2). Auto-fallback on 5xx/region-error to `google/gemini-2.5-flash-image` (original Nano Banana)
    rationale: User explicitly chose Nano Banana 2 over the Pro variant on 2026-04-29 ("actually, i would like nano banana 2 not pro"). Marketing positioning: "Pro-level quality at Flash speed" — the cost/quality tradeoff favors Nano Banana 2 for a 10-slide deck where the deck is regenerated multiple times during authoring. Original Nano Banana (gemini-2.5-flash-image) is the cheapest deeper fallback. All three are `-preview`-tagged as of April 2026; no stable non-preview variants exist yet — pin the slug and version-check.
  - id: D-04
    choice: API endpoint = `https://openrouter.ai/api/v1/chat/completions` (OpenAI-compat chat completions, NOT a separate /images route). Body must include `"modalities": ["image", "text"]` and `"image_config": {"aspect_ratio": "16:9", "image_size": "1K"}`. Image returned as base64 data URL at `choices[0].message.images[].image_url.url`
    rationale: Verified via OpenRouter docs and minimal-curl call shape. Default to "1K" image_size (~$0.05/image) for content slides; "2K" only on title/hero slide (~$0.10–0.20). 4K too expensive for 10-slide decks.
  - id: D-05
    choice: Auth = `OPENROUTER_API_KEY` env var. No fallback key handling. If missing, skill prints a clear setup message and exits the image step (deck still renders without images)
    rationale: User said "I have credits there" implying the key is already set in their environment. Hardcoded fallbacks are an antipattern (security smell, hides config drift). Soft-failing the image step keeps the deck-build path resilient.
  - id: D-06
    choice: Image generation runs as a SEPARATE batch pass, invoked by the user explicitly (`generate_images.sh <deck.html>`) AFTER the deck is drafted and reviewed. Not interactive per slide, not auto-on-every-build
    rationale: Burning $0.50–2.00 in API credits on every iteration is wasteful. Drafting + content review is fast and free; image gen is the costly step that should be deliberate. Users can re-run it after content tweaks. Also, generating images per-slide-as-you-author breaks flow.
  - id: D-07
    choice: Image-role heuristic per slide = ≤2 content elements → full-bleed background; 3–6 elements → contextual side image (40/60 split with content); ≥7 elements OR explicit `data-no-image` → no image
    rationale: Title slide and section dividers are sparse → benefit most from a hero image. Mid-density slides (3-card grids, 4-row lists) tolerate a side image. Dense card grids and survey-data slides become unreadable with images behind them. The heuristic reads the slide HTML's element count, no manual tagging required.
  - id: D-08
    choice: Image prompt = auto-generated from each slide's `data-image-prompt` attr (if present, user-provided override) OR the slide's eyebrow + h2 + a brand prompt suffix. Brand suffix differs by palette mode (light vs dark) and image role (background vs contextual)
    rationale: Two layers of control: zero-config default works out of the box; user can override per slide by adding `data-image-prompt` to the slide's `<section>`. Brand suffix keeps imagery consistent across the deck — pulled from the exemplar's visual style ("editorial illustration, monochrome blue-on-white, anatomical line-art" for light mode; "moody photographic, dark navy and red accent, scientific" for dark mode).
  - id: D-09
    choice: Generated images cached at `<deck-folder>/images/<slide-id>.png`. Re-runs reuse cache unless user passes `--refresh` or the slide's prompt has changed (detected via prompt-hash sidecar `.<slide-id>.prompt`)
    rationale: Image gen is the only paid step in the pipeline; caching protects against accidental re-billing. Hash-based invalidation means users can edit prompts and only the changed slides regenerate. Sidecar files keep the cache transparent (versionable in git if user wants reproducibility, gitignorable if they don't).
  - id: D-10
    choice: API failure mode = soft fail. On any 4xx/5xx, the skill logs the error to `<deck>/images/.errors.log`, leaves the slide image-less, and continues. The deck still opens cleanly with no missing-image broken icons (CSS hides the image element when `src` is empty)
    rationale: A 10-slide deck shouldn't fail because slide 7's API call hit a transient region error. User can re-run image gen for failed slides selectively. Hard-failing on first error wastes the previously-paid-for successful images.
  - id: D-11
    choice: Brand registers as ONE preset "Brand · Pharma Scientific" with two palette MODES: `light-clinical` (bg `#fafafa`, accent `#2563eb`, text near-black) and `dark-minimal` (bg `#0a0a0a`, accent `#ef4444`, text white). The frontend-slides upstream 12 presets are NOT included; this skill is brand-locked
    rationale: User established palette is iteratable but the system isn't. Two confirmed modes capture both their accepted iterations. Not bundling 12 generic presets keeps the skill focused on what they actually use; if they ever want a generic deck they can use frontend-slides directly.
  - id: D-12
    choice: Don't modify upstream frontend-slides skill (installed via plugin marketplace, read-only) or the in-repo marp-slides skill. New skill cross-references both via SKILL.md links
    rationale: Stated requirement. Frontend-slides is upstream and shouldn't be forked; modifications would silently revert on plugin update. Marp-slides is working and owns its niche (editable PPTX); coexistence beats consolidation.
  - id: D-13
    choice: Brand CSS shipped INLINE in the generated HTML, captured verbatim from `ai-safety-pharmacology-frontend/index.html`'s `<style>` block (the user's accepted artefact). Use the legacy variable aliases (`--accent-warm: var(--accent)`, etc.) so reskinning between modes is one variable change
    rationale: Verbatim transfer means future sessions inherit the exact brand the user signed off on, not an approximation. Aliases are the durable signal — saved ~30 edits per reskin during this project.
  - id: D-14
    choice: Runtime dependencies = bash, curl, python3 (with stdlib only — no python-pptx or pillow). No Node, no npm install. Optional: pandoc + Marp CLI ONLY if user invokes the PPTX/HTML-from-marp path
    rationale: The skill must run on a fresh machine without dependency dance. Bash + curl + python3 are universal; image gen needs only base64 decoding (stdlib). Heavier deps belong to the marp-slides skill which already mandates them.
  - id: D-15
    choice: Slide elements that opt out of image processing use `data-no-image` attribute on the `<section>`. Slides that override the auto-prompt use `data-image-prompt="..."`. No other custom attributes
    rationale: Two attributes is the minimum surface area for control; everything else is auto-derived. Keeps the deck markup readable and the skill's logic simple.
  - id: D-16
    choice: Image generation script writes a cost summary at end of run (`Generated N images, ~$X.XX estimated cost`) using $0.05/1K image and $0.15/2K image as planning estimates. Warn before run if N > 10 images expected
    rationale: User mentioned "I have credits" but estimating cost prevents accidental over-spending. Threshold of 10 images is the typical 10-slide deck baseline; anything more (e.g., a 30-slide deck) should prompt confirmation.
tasks:
  - id: T-01
    action: Create skill folder structure at `.claude/skills/branded-slides/` with empty subfolders `templates/`, `scripts/`, `assets/icons/`, `docs/`
    verify: Directory exists with the four subfolders. `tree -L 3 .claude/skills/branded-slides/` shows the layout.
    depends_on: []
  - id: T-02
    action: Write `.claude/skills/branded-slides/SKILL.md` with frontmatter (name=branded-slides, description triggers on "make a presentation/deck/talk/slides" with brand emphasis), phase structure (Phase 0 detect mode, Phase 1 content + palette discovery via single AskUserQuestion call, Phase 2 generate brand-locked HTML, Phase 3 optional `generate_images.sh` invocation, Phase 4 deliver). Cross-reference marp-slides for PPTX path. Include the workflow section that mirrors frontend-slides' phase-by-phase structure but with the brand pre-selected
    verify: SKILL.md exists at the path; running `head -30 SKILL.md` shows valid YAML frontmatter and a phase outline. The description field starts with "Author beautiful HTML decks with the project's locked brand..."
    depends_on: [T-01]
  - id: T-03
    action: Write `.claude/skills/branded-slides/BRAND.md` capturing the durable brand signals from `feedback_deck_style.md` and the exact `:root` CSS block from `ai-safety-pharmacology-frontend/index.html`. Include both palette modes (light-clinical + dark-minimal), the typography ranges, the no-italic emphasis rule, the minimal-chrome rule, and the verbatim variable-alias pattern
    verify: BRAND.md exists; contains the verbatim `:root { --bg-primary: ...; }` block for both modes and the durable-signals list. Running `grep -c "Space Grotesk" BRAND.md` returns ≥ 1.
    depends_on: [T-01]
  - id: T-04
    action: Write `.claude/skills/branded-slides/templates/template.html` — a single self-contained HTML file with the full brand `<style>` block (verbatim from brand artefact), a placeholder `<!-- SLIDES -->` marker between `<body>` tags, a placeholder `<!-- DATA-PALETTE -->` for palette mode, and the inline `SlidePresentation` class JS (verbatim from brand artefact, the `replaceChildren()` version that's hook-safe)
    verify: Template file exists. `grep -c "SlidePresentation" templates/template.html` returns ≥ 1. Opening it directly in a browser renders an empty deck shell with no console errors.
    depends_on: [T-01, T-03]
  - id: T-05
    action: Write `.claude/skills/branded-slides/templates/slide-patterns.md` — a markdown file documenting the four slide layout patterns the brand uses (title slide, three-up cards, four-up grid, row-list, pull-quote, timeline, ring/donut chart, closing slide). For each pattern: HTML snippet + when-to-use + content-density tier (which determines image-role mapping)
    verify: File exists; contains snippets for at least 6 distinct layouts. `grep -c "^## " templates/slide-patterns.md` returns ≥ 6.
    depends_on: [T-01]
  - id: T-06
    action: Write `.claude/skills/branded-slides/scripts/generate_images.sh` — bash script that takes an HTML deck path as $1, parses each `<section class="slide">` for content-density (counts cards, rows, headings), computes image role (`background`|`contextual`|`none`), builds a prompt from `data-image-prompt` OR `eyebrow + h2 + brand-suffix`, calls OpenRouter `https://openrouter.ai/api/v1/chat/completions` with model `google/gemini-3.1-flash-image-preview`, decodes base64 from `choices[0].message.images[].image_url.url`, writes to `<deck-folder>/images/<slide-id>.png`, caches via prompt-hash sidecar, and falls back to `google/gemini-2.5-flash-image` on 5xx
    verify: Script exists and is executable. Running with no args prints usage. Running with a fake `--dry-run` flag on a real deck path enumerates slides and shows planned prompts WITHOUT calling the API. With a real `OPENROUTER_API_KEY` set and `--limit 1`, it generates exactly one image, caches it, and the deck reloads to show the image embedded.
    depends_on: [T-01, T-04]
  - id: T-07
    action: Write `.claude/skills/branded-slides/scripts/inject_images.py` — Python3 script (stdlib only) invoked by `generate_images.sh` after image generation; rewrites the deck HTML to add `<img class="slide-bg">` (for background role) or `<aside class="slide-image">` (for contextual role) into each slide that has a cached image. Idempotent: re-running doesn't duplicate elements
    verify: Script exists. Running on a deck with 0 cached images produces no changes. Running on a deck with 1 cached image adds exactly one image element to the matching slide and exits 0. Running again is a no-op.
    depends_on: [T-06]
  - id: T-08
    action: Add CSS rules in `templates/template.html` for `.slide-bg` (full-bleed image with overlay, opacity by palette mode) and `.slide-image` (40% width, contextual side image with rounded corners). Both rules must respect viewport-base.css and degrade gracefully when image fails to load
    verify: Template has both `.slide-bg` and `.slide-image` rules. Inserting a sample `<img class="slide-bg" src="">` produces no visual artifact (broken icon hidden). Inserting a real image renders full-bleed with the brand-mode overlay (dark mode = ~70% black overlay, light mode = ~80% white overlay).
    depends_on: [T-04]
  - id: T-09
    action: Write `.claude/skills/branded-slides/templates/starter-deck.html` — a 10-slide example deck pre-filled with a generic structure (title, problem, three forces, application 1, application 2, application 3, data slide, regulatory timeline, challenges, future + closing) using brand classes (eyebrow, section-head, three-up, row-list, ring, timeline, closing-quote). Each slide has a meaningful `data-image-prompt` so the user can run `generate_images.sh` on it as a smoke test
    verify: File exists. Opening in browser renders 10 visible scroll-snap slides with the brand styling and no console errors. Running `generate_images.sh starter-deck.html --dry-run` enumerates 10 prompts.
    depends_on: [T-04, T-05]
  - id: T-10
    action: Write `.claude/skills/branded-slides/docs/PPTX_EXPORT.md` — short doc cross-referencing the in-repo `marp-slides` skill for editable-PowerPoint output. Show the exact pandoc command users should run if they want PPTX, and warn them that animations/scroll-snap don't transfer to PPTX
    verify: File exists; references `.claude/skills/marp-slides/` and includes a runnable pandoc command snippet.
    depends_on: [T-01]
  - id: T-11
    action: Write `.claude/skills/branded-slides/docs/IMAGE_PROMPT_GUIDE.md` — short doc explaining (a) auto-prompt construction, (b) when to use `data-image-prompt` override, (c) the brand suffix for each palette mode (verbatim — these need to be reproducible across sessions), (d) cost guidance ($0.05 1K / $0.15 2K), (e) how to refresh a single slide
    verify: File exists; contains both palette-mode brand suffixes verbatim.
    depends_on: [T-01]
  - id: T-12
    action: Update repo `README.md` to add a one-line entry for the new skill alongside the existing marp-slides entry, with a one-sentence "what it does differently" pointer
    verify: README diff shows a new bullet/line referencing `branded-slides`. `grep -c "branded-slides" README.md` returns ≥ 1.
    depends_on: [T-01, T-02]
  - id: T-13
    action: Smoke test: from a clean state, invoke the skill via Claude Code by saying "make a one-pager about X using branded-slides". Confirm the skill triggers (its description matches), it asks the palette-mode question, generates a 10-slide deck file with the brand baked in, and the deck opens in the browser with no console errors. Image gen is OPTIONAL in this smoke test.
    verify: Manual: Claude Code invokes the skill; output deck is at the expected path; deck opens; brand `--accent` is the chosen palette's accent; nav dots and progress bar work; no console errors. Document any deviations in `docs/SMOKE_TEST_RESULTS.md`.
    depends_on: [T-02, T-03, T-04, T-05, T-09]
  - id: T-14
    action: Smoke test: with `OPENROUTER_API_KEY` set, run `generate_images.sh starter-deck.html --limit 2` and verify 2 images are generated, cached, and embedded in the deck. Re-run without `--limit` and verify cache is reused (no new API calls; should complete in <1s)
    verify: Manual: First run generates exactly 2 PNGs in `images/`; deck shows them. Second run logs "cache hit" for both, makes 0 API calls, deck unchanged. Cost summary printed at end of first run.
    depends_on: [T-06, T-07, T-09]
open_questions:
  - "[Stated] The PPTX exemplar is technically a NotebookLM-generated 'whole-slide-as-image' deck (14 full-bleed PNGs with text baked in). Our locked scope picked the contextual-side path (Image roles: background OR contextual side image). Is the contextual-side approach still desired, or does the user actually want full-slide-as-image generation matching the exemplar literally? If literal, T-08's `.slide-bg` becomes the dominant pattern and editable text overlays may need to be removed entirely on image-rich slides. Recommend confirming during T-13 smoke test by showing both styles."
  - "[Decision] D-09 caches images at `<deck-folder>/images/`. Should this be `.gitignored` by default? Pros of committing: reproducible deck output across machines, no re-billing on team handoff. Pros of ignoring: doesn't bloat repo (each PNG is 0.5–2 MB; 10 slides × 1 MB = 10 MB per deck). Default to committed for now; document the choice in BRAND.md so users can flip it."
  - "[Decision] D-13 ships the SlidePresentation class verbatim. The class is ~80 lines of inline JS; if the skill is ever re-skinned for a non-scroll-snap output (e.g., PowerPoint), this code is dead weight. Acceptable for now since HTML is the primary output; revisit if PPTX export becomes a first-class path."
  - "[Coverage] No task explicitly verifies the brand defaults match the user's accepted artefact byte-for-byte. T-04 captures the CSS verbatim, but a regression-style diff between `templates/template.html`'s `<style>` block and `ai-safety-pharmacology-frontend/index.html`'s `<style>` block isn't part of any verify step. Consider adding a `scripts/verify_brand.sh` that diffs the two and exits non-zero if they drift — but that's a quality-of-life improvement, not blocking shipment."
---

## Summary

A new project-scoped Claude Code skill at `.claude/skills/branded-slides/` that combines the patterns from the upstream `frontend-slides` skill (animation-rich self-contained HTML decks) with the in-repo `marp-slides` skill (cross-referenced for optional editable-PowerPoint output), bakes in the brand the user iterated to over six redirects on the AI-in-Safety-Pharmacology deck, and integrates OpenRouter's Nano Banana 2 (`google/gemini-3.1-flash-image-preview`) for context-aware AI image generation per slide. The skill ships a starter deck, a generation script, an injection script, and documentation. Image gen runs as a separate batch pass (not on every build) with prompt-hash caching to protect against accidental re-billing. The brand is shipped verbatim from the user's accepted artefact, with two palette modes (light-clinical + dark-minimal) selectable per deck.

## Scope

**Stated:**

- Read the upstream frontend-slides skill and learn its patterns
- Combine it with the in-repo marp-slides skill (coexist, don't duplicate)
- Bake the iterated color + text style as a brand guideline in the new skill
- Integrate OpenRouter for AI image generation (originally specified Nano Banana Pro; user revised on 2026-04-29 to Nano Banana 2)
- Image generation must be context-aware (uses slide content)
- Two image roles supported: full-bleed background OR contextual side image
- Match the visual density of the AI_in_Safety_Pharmacology_and_Toxicology.pptx exemplar

**Inferred:**

- Skill name: `branded-slides`; lives at `.claude/skills/branded-slides/`
- Primary output: HTML; PPTX opt-in via cross-reference to marp-slides
- Image gen runs as a separate batch pass, not interactively per slide
- Image prompts auto-generated from slide eyebrow + h2 + brand suffix; user can override per slide via `data-image-prompt`
- Image-role heuristic: ≤2 elements → background, 3–6 → contextual, ≥7 → none
- Generated images cached at `<deck>/images/<slide-id>.png` with prompt-hash invalidation
- API failure = soft fail (deck renders, missing image silent, error logged)
- Brand registers as ONE preset "Brand · Pharma Scientific" with two palette modes; the upstream 12 presets are NOT bundled
- `OPENROUTER_API_KEY` env var, no fallback key handling
- The upstream frontend-slides skill and the in-repo marp-slides skill are NOT modified
- Runtime: bash, curl, python3 (stdlib only). No Node/npm. Optional: pandoc + Marp CLI for the PPTX path

**Out of scope:**

- Modifying the upstream frontend-slides skill (installed via plugin marketplace)
- Modifying the in-repo marp-slides skill (must coexist)
- Auto-deploying decks to Vercel
- Image post-processing (upscaling, cropping, retouching)
- Animations/transitions beyond what frontend-slides provides
- Auto-regenerating the existing `ai-safety-pharmacology-frontend/index.html` deck with images (separate follow-up after the skill exists)
- Multi-language / i18n support
- A slide-level UI for editing image prompts in real-time (users edit the deck file post-hoc)
- PowerPoint-specific styling beyond what marp-slides already does

## Decisions

- **D-01:** Skill name = `branded-slides`; lives at `.claude/skills/branded-slides/` — Stated location; name reflects "brand baked in" generally enough to serve future scientific decks.
- **D-02:** Primary output = HTML; PPTX = opt-in via marp-slides cross-reference — Image gen is HTML-native; marp-slides already owns editable-PPTX; coexistence over duplication.
- **D-03:** OpenRouter slug = `google/gemini-3.1-flash-image-preview` (Nano Banana 2); fallback `google/gemini-2.5-flash-image` (original Nano Banana) — User explicitly chose Nano Banana 2 over Pro on 2026-04-29 ("actually, i would like nano banana 2 not pro"). Cost/quality tradeoff favors Flash for an iteratively re-generated 10-slide deck.
- **D-04:** API endpoint = `https://openrouter.ai/api/v1/chat/completions` with `modalities: ["image","text"]`; default `image_size: "1K"`, hero `"2K"` — Image returned as base64 data URL; "1K" is ~$0.05/image (target cost for 10-slide decks).
- **D-05:** Auth = `OPENROUTER_API_KEY` env var, no fallback — User has the key; hardcoding fallbacks is an antipattern.
- **D-06:** Image gen is a separate batch pass (`generate_images.sh`) invoked by user, not auto-on-build — Drafting is fast/free; image gen is the costly step that should be deliberate.
- **D-07:** Image-role heuristic: ≤2 elements → background, 3–6 → contextual, ≥7 → none — Title/section slides benefit from hero; mid-density tolerates a side; dense grids overflow with images.
- **D-08:** Prompt = `data-image-prompt` override OR auto from eyebrow + h2 + brand suffix; brand suffix differs by palette + role — Two layers of control; brand suffix keeps imagery consistent across deck.
- **D-09:** Images cached at `<deck>/images/<slide-id>.png`; sidecar prompt-hash for invalidation — Caching protects against re-billing; hash invalidation lets users edit prompts and only regenerate changed slides.
- **D-10:** API failure = soft fail with error logged; deck still renders — Transient errors shouldn't fail a 10-slide deck; selective re-run for failed slides.
- **D-11:** Brand = ONE preset "Brand · Pharma Scientific" with two palette modes (light-clinical + dark-minimal) — Two confirmed user iterations; no need to bundle 12 generic presets.
- **D-12:** No modifications to upstream frontend-slides or in-repo marp-slides — Stated requirement; cross-reference only.
- **D-13:** Brand CSS shipped verbatim from `ai-safety-pharmacology-frontend/index.html`'s `<style>` block, including legacy variable aliases — Verbatim transfer = exact brand inheritance; aliases are the durable signal that saved ~30 edits per reskin.
- **D-14:** Runtime = bash, curl, python3 stdlib. No Node. Optional: pandoc + Marp for PPTX path — Universal toolchain; heavy deps belong to the marp-slides skill.
- **D-15:** Two slide attributes: `data-no-image` (opt-out) and `data-image-prompt` (override). Nothing else — Minimum surface area for control.
- **D-16:** Cost summary at end of every image run; warn before run if N > 10 expected — Prevent accidental over-spending despite credits.

## Tasks

### T-01 — Create skill folder structure

- **Action:** Create `.claude/skills/branded-slides/` with subfolders `templates/`, `scripts/`, `assets/icons/`, `docs/`
- **Verify:** Directory exists with the four subfolders; `tree -L 3 .claude/skills/branded-slides/` shows the layout
- **Depends on:** none

### T-02 — Write SKILL.md with phase flow

- **Action:** Create `SKILL.md` with frontmatter (name, description triggering on slide/deck/talk/presentation requests with brand emphasis) and a Phase 0–4 outline (detect mode, content + palette discovery via single AskUserQuestion call, brand-locked HTML generation, optional image-gen batch pass, deliver). Cross-reference marp-slides for PPTX
- **Verify:** SKILL.md exists; valid YAML frontmatter; description starts with "Author beautiful HTML decks with the project's locked brand…"
- **Depends on:** T-01

### T-03 — Write BRAND.md

- **Action:** Capture durable brand signals from `feedback_deck_style.md` and the verbatim `:root` CSS block from `ai-safety-pharmacology-frontend/index.html`. Both palette modes (light-clinical + dark-minimal), typography ranges, no-italic rule, minimal-chrome rule, alias pattern
- **Verify:** BRAND.md exists; contains verbatim `:root { ... }` blocks for both modes; `grep -c "Space Grotesk" BRAND.md` returns ≥ 1
- **Depends on:** T-01

### T-04 — Write templates/template.html (brand-locked HTML shell)

- **Action:** Single self-contained HTML file with full brand `<style>` block (verbatim from artefact), `<!-- SLIDES -->` and `<!-- DATA-PALETTE -->` placeholders, inline `SlidePresentation` class (the `replaceChildren()` hook-safe version)
- **Verify:** Template exists; opens in browser as empty deck shell with no console errors; `grep -c "SlidePresentation" templates/template.html` returns ≥ 1
- **Depends on:** T-01, T-03

### T-05 — Write templates/slide-patterns.md

- **Action:** Document the brand's slide layout patterns: title, three-up cards, four-up grid, row-list, pull-quote, timeline, ring/donut, closing. Per pattern: HTML snippet + when-to-use + content-density tier
- **Verify:** File exists; ≥ 6 distinct layouts; `grep -c "^## " templates/slide-patterns.md` returns ≥ 6
- **Depends on:** T-01

### T-06 — Write scripts/generate_images.sh

- **Action:** Bash script: parse deck HTML for slide content-density, compute image role, build prompt (override or auto), call OpenRouter chat-completions with `google/gemini-3.1-flash-image-preview`, decode base64, save to `images/<slide-id>.png`, cache via prompt-hash, fallback to `google/gemini-2.5-flash-image` on 5xx
- **Verify:** Script is executable; no-args prints usage; `--dry-run` enumerates planned prompts without API calls; with `OPENROUTER_API_KEY` and `--limit 1`, generates exactly one image and embeds it
- **Depends on:** T-01, T-04

### T-07 — Write scripts/inject_images.py

- **Action:** Python3 stdlib-only script invoked by `generate_images.sh` after image gen; idempotently rewrites the deck HTML to add `<img class="slide-bg">` or `<aside class="slide-image">` per cached image
- **Verify:** Script exists; runs as no-op on deck with no cached images; adds exactly one element on a deck with one cached image; re-running is a no-op
- **Depends on:** T-06

### T-08 — Add image CSS rules to template

- **Action:** Add `.slide-bg` (full-bleed image with palette-aware overlay) and `.slide-image` (40% width contextual) rules to `templates/template.html`. Both must respect viewport-base.css and degrade gracefully when image is missing
- **Verify:** Template has both rules; broken-image element is visually hidden; real image renders full-bleed with palette-mode overlay (dark = ~70% black, light = ~80% white)
- **Depends on:** T-04

### T-09 — Write templates/starter-deck.html

- **Action:** 10-slide example deck pre-filled with brand structure (title → problem → three forces → app 1 → app 2 → app 3 → data → regulatory timeline → challenges → future). Each slide has `data-image-prompt` for smoke testing
- **Verify:** Renders 10 visible scroll-snap slides; no console errors; `generate_images.sh --dry-run` enumerates 10 prompts
- **Depends on:** T-04, T-05

### T-10 — Write docs/PPTX_EXPORT.md

- **Action:** Short cross-reference to in-repo `marp-slides` skill for editable PowerPoint output; runnable pandoc command snippet; caveat about animations not transferring
- **Verify:** File exists; references `.claude/skills/marp-slides/`; contains a pandoc command
- **Depends on:** T-01

### T-11 — Write docs/IMAGE_PROMPT_GUIDE.md

- **Action:** Document auto-prompt construction, `data-image-prompt` override usage, brand suffix verbatim per palette mode, cost guidance, single-slide refresh procedure
- **Verify:** File exists; contains both palette-mode brand suffixes verbatim
- **Depends on:** T-01

### T-12 — Update repo README.md

- **Action:** Add a one-line entry for the new skill alongside marp-slides; one-sentence what-it-does-differently pointer
- **Verify:** Diff shows new bullet referencing `branded-slides`; `grep -c "branded-slides" README.md` returns ≥ 1
- **Depends on:** T-01, T-02

### T-13 — End-to-end smoke test: skill triggers and generates a deck

- **Action:** From clean state, invoke via "make a one-pager about X using branded-slides"; confirm skill triggers, asks palette mode, generates a 10-slide deck with brand baked in, deck opens with no errors. Image gen optional in this test
- **Verify:** Manual; document deviations in `docs/SMOKE_TEST_RESULTS.md`
- **Depends on:** T-02, T-03, T-04, T-05, T-09

### T-14 — End-to-end smoke test: image generation and caching

- **Action:** With `OPENROUTER_API_KEY` set, run `generate_images.sh starter-deck.html --limit 2`; verify 2 images generated, cached, embedded; re-run without `--limit` and verify cache reuse (0 API calls, <1s)
- **Verify:** First run generates 2 PNGs and shows in deck; second run logs "cache hit", makes 0 API calls, deck unchanged. Cost summary printed
- **Depends on:** T-06, T-07, T-09

## Open Questions

- **[Stated]** The PPTX exemplar is technically a NotebookLM-generated "whole-slide-as-image" deck (14 full-bleed PNGs with text baked in). Our locked scope picked the contextual-side path. Is the contextual-side approach still desired, or does the user actually want full-slide-as-image matching the exemplar literally? Recommend confirming during T-13 smoke test by showing both styles in the starter deck so the user can pick.
- **[Decision]** D-09 caches images at `<deck>/images/`. Should this be `.gitignored` by default? Default to committed for reproducibility; document the choice in BRAND.md so users can flip it.
- **[Decision]** D-13 ships the `SlidePresentation` class verbatim (~80 lines of inline JS). If the skill is ever re-skinned for a non-scroll-snap output, this code is dead weight. Acceptable for now since HTML is primary; revisit if PPTX becomes first-class.
- **[Coverage]** No task explicitly diffs `templates/template.html`'s `<style>` block against `ai-safety-pharmacology-frontend/index.html`'s `<style>` block to catch brand drift. Consider adding `scripts/verify_brand.sh` as a quality-of-life follow-up; not blocking shipment.
