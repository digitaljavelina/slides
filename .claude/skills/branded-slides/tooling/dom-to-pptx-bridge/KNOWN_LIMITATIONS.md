# dom-to-pptx bridge — known limitations

This bridge produces a high-fidelity, native-shape, editable `.pptx` from a `branded-slides` HTML deck via headless Chromium + dom-to-pptx. It hits roughly **80% fidelity** to the source HTML. The remaining gap is architectural, not a bug list.

## What works well

- Brand vocabulary survives: `.three-up` cards with eyebrows + accent strips, row-list with icons, pull-quote with full-bleed background, four-up grid, timeline, accent-colored `<em>` text.
- AI-generated imagery embeds at full resolution (28 native shapes per typical 11-slide deck).
- Dark and light palettes carry through (bg, text, accent).
- Native widescreen 13.333″ × 7.5″ slide dimensions.
- Body fonts at slide-appropriate sizes (~16 pt body, ~67 pt title).
- Output is fully editable in PowerPoint, Keynote, and LibreOffice Impress.

## What doesn't quite match the HTML

These are properties of _any_ DOM-to-PPTX converter, not solvable without forking the library or restructuring the brand HTML.

### 1. `<aside class="slide-image">` doesn't fill its parent box

The brand's image asides use `width: 28%; aspect-ratio: 4/5` on the parent and `width: 100%; height: 100%; object-fit: cover` on the inner `<img>`. dom-to-pptx writes images at their **intrinsic ratio** (the source PNG's natural dimensions) rather than honoring the CSS-layout dimensions. Result: the AI-generated PNG renders at its native ratio inside the parent box, leaving empty bands.

**Why it can't be fixed cleanly:** `aspect-ratio` is computed by the browser layout engine at render time; PPTX has no equivalent. `object-fit: cover` is a paint-time directive that requires rasterization to express in PPTX. dom-to-pptx skips both.

### 2. Vertical alignment between text columns and image asides drifts

In HTML, `.slide-content` centers via `flex; justify-content: center`, and the image aside uses `top: 50%; transform: translateY(-50%)`. Both center vertically, but they're computed by _different_ layout systems. Sub-pixel differences in headless-Chromium layout become visible misalignment in the PPTX.

### 3. Cascading text properties don't inherit cleanly

dom-to-pptx walks each element in isolation. Properties that depend on CSS cascade (e.g. `color: var(--text-secondary)` on a parent shining through to an unstyled child) sometimes need explicit per-element values. The bridge already handles `<body>` background propagation; other cascade dependencies may surface in other brands.

## When to pick a different approach

If the brand depends heavily on layout-level CSS (`aspect-ratio`, `object-fit`, flex centering against absolute siblings, CSS grid with named tracks), DOM-to-PPTX has a hard ceiling. Two alternatives that close the visual gap at the cost of editability:

- **Playwright screenshot per slide → embed as full-bleed image in python-pptx.** Pixel-perfect. Slides become raster images with editable speaker notes only.
- **Hybrid: rendered-PNG background + editable title text-box overlay.** Compromise between fidelity and edit access.

The pandoc-based path (`scripts/html_to_pptx.py` + pandoc) remains in the skill as a no-Node-dependencies fallback for users who want plain text + bullets without imagery polish.

## Tested against

- `decks/claude-on-proxmox/index.html` (11 slides, 9 AI images, dark-minimal palette) on 2026-05-01 — produced a 17 MB PPTX that opens cleanly in Keynote and PowerPoint with all brand vocabulary visible.
