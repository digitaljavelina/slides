# Image prompt guide

How `scripts/generate_images.sh` builds prompts for OpenRouter Nano Banana 2 (`google/gemini-3.1-flash-image-preview`), and how to override them per slide.

## TL;DR

For most slides, do nothing — the script auto-derives a reasonable prompt from the slide's eyebrow and `<h2>`. Only set `data-image-prompt="…"` when the auto-prompt would produce something generic (e.g., the eyebrow is "Future directions" — not enough subject matter).

## Auto-prompt construction

For each slide that doesn't have `data-image-prompt` and doesn't have `data-no-image`, the script builds:

```
<eyebrow text>. <h2 plain text>. <brand suffix>
```

Example, slide 4 of the AI-in-Safety-Pharmacology deck:

- Eyebrow: `Cardiac safety`
- H2: `Stratifying risk earlier in development.`
- Built prompt: `Cardiac safety. Stratifying risk earlier in development. <brand suffix>`

The brand suffix differs by **palette mode** and **image role**.

## Brand suffixes (verbatim)

These are pinned in `scripts/generate_images.sh`. Treat them as part of the brand. Don't ad-lib — consistent imagery across a deck is what makes the deck feel composed rather than collaged.

### Light Clinical · background role

```
Editorial illustration suitable as a slide background. Solid off-white background (#fafafa), single deep-blue accent (#2563eb). Minimal, photographic or illustrated line-art. Anatomical or scientific subjects rendered as clean monochrome line-art with selective blue accent fills. No text. No watermarks. 16:9 aspect.
```

### Light Clinical · contextual role

```
Editorial illustration for the right side of a slide. White or off-white background, single deep-blue accent (#2563eb). Subject centered with breathing room around it. Anatomical line-art, scientific diagram, or photographic histology. No text overlays. 16:9 aspect, but composed so the left half of the frame is empty negative space (text will overlay there).
```

### Dark Minimal · background role

```
Cinematic editorial photograph or illustration suitable as a slide background. Near-black background (#0a0a0a), single vivid red accent (#ef4444) used sparingly. Moody, low-key lighting. Scientific subject (anatomy, cell, instrument, abstract data shape) rendered photographically or as silhouette. No text. No watermarks. 16:9 aspect.
```

### Dark Minimal · contextual role

```
Cinematic editorial illustration for the right side of a slide. Dark near-black background, single vivid red accent (#ef4444). Subject offset to the right of frame; left half is empty dark negative space (text will overlay there). Photographic or stylized; no text. 16:9 aspect.
```

## Per-slide override

When the auto-prompt would produce something generic, override with `data-image-prompt`:

```html
<section
  class="slide"
  data-title="Future directions"
  data-image-prompt="abstract horizon at twilight, scientific instruments silhouetted against the sky, single red accent, cinematic"
>
  …
</section>
```

The override **replaces** the eyebrow + h2 portion. The brand suffix is still appended automatically — don't include it in your override; the script adds it.

If you want full control (no brand suffix appended), set `data-image-prompt-raw` instead. The script will use it verbatim. Use sparingly; you lose visual consistency with the rest of the deck.

## When NOT to use auto-prompts

Set `data-no-image` on the slide's `<section>` when:

- The slide is already visually dense (4-up cards, full ring chart with metadata table, code listing).
- The slide's content is data that doesn't translate to imagery (a table of stats, a regulatory timeline with dates).
- The slide's headline emphasis is the visual itself (a big pull-quote — adding an image would dilute the impact).

Use `data-no-image` over `data-image-prompt=""` (empty string). The empty-string form still triggers the auto-prompt path; the attr presence is what disables it.

## Image-role mapping

The script picks role based on content density:

| Content elements in slide         | Role assigned | What the script generates                                                                                                                 |
| --------------------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 0–2 (title, pull-quote, big-stat) | `background`  | Full-bleed `<img class="slide-bg">` with palette-mode overlay (~70% black for dark, ~80% white for light) so text remains readable on top |
| 3–6 (cards, rows, timeline items) | `contextual`  | `<aside class="slide-image">` taking ~40% width on the right; content reflows to 60%                                                      |
| ≥7 OR `data-no-image`             | `none`        | No image generated; slide stays text-only                                                                                                 |

You can override the role with `data-image-role="background"` or `data-image-role="contextual"` on the section if the auto-classification picks wrong.

## Cost guidance

Nano Banana 2 (`google/gemini-3.1-flash-image-preview`) is meaningfully cheaper than Pro. Approximate planning numbers (these will be confirmed by the cost summary the script prints at end of run):

| Image size       | Approximate cost | When to use                                                                                      |
| ---------------- | ---------------- | ------------------------------------------------------------------------------------------------ |
| `"1K"` (default) | a few cents      | Content slides — 90% of the deck                                                                 |
| `"2K"`           | ~2× the 1K cost  | Title slide, hero pull-quote                                                                     |
| `"4K"`           | ~4×              | Don't, unless the deck will be displayed on a large screen and a single slide is the centerpiece |

The script defaults to `"1K"`. Add `--hero-2k` to generate the title slide at 2K.

A 10-slide deck with 7 images at 1K should cost under a quarter, at most. Re-runs hit the prompt-hash cache and cost $0.

## Refreshing one slide

To regenerate the image for one slide (e.g., you edited its `data-image-prompt`):

```bash
# Delete its cached image and prompt-hash sidecar
rm decks/<slug>/images/<slide-id>.png decks/<slug>/images/.<slide-id>.prompt
# Re-run the script
scripts/generate_images.sh decks/<slug>/index.html
```

Or with a flag:

```bash
scripts/generate_images.sh decks/<slug>/index.html --refresh-slide <slide-id>
```

To regenerate **everything** (rare; use after changing the brand suffix):

```bash
scripts/generate_images.sh decks/<slug>/index.html --refresh
```

## Troubleshooting

- **Empty / broken images on every slide** → check `OPENROUTER_API_KEY`. The script prints a setup message if it's missing, but if it's set to an invalid key, you'll see 401s in `decks/<slug>/images/.errors.log`.
- **One slide failed** → it's logged in `.errors.log`. Re-run the script; the cached good slides skip. If a particular prompt keeps failing, simplify it (Nano Banana 2 occasionally returns 4xx on prompts with too many constraints).
- **Image looks off-brand** → first check the palette mode in `<body data-palette="…">`. If a contextual slide's image has its subject on the _left_ (covering where text goes), regenerate — the brand suffix tells the model to keep the left half empty, but it's not infallible.
- **Script wants to regenerate everything** → check that the brand suffix in `scripts/generate_images.sh` hasn't been edited. Editing the suffix invalidates every prompt-hash on next run. That's intentional, but it'll cost a full deck's worth of API calls.
