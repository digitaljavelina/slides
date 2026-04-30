# BRAND.md — branded-slides

The single source of truth for what the brand IS. Captures decisions the user iterated to over six redirects on the AI-in-Safety-Pharmacology deck (2026-04-29). Treat this file as authoritative; if you change the brand, update here first, then propagate to `templates/template.html`.

## Durable signals

These held across every theme iteration the user accepted. They are NOT negotiable per-deck — they are the brand.

| Signal                | Value                                                                                            | Quote / origin                                                                                                                                                                                |
| --------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Display font**      | Space Grotesk (600/700)                                                                          | "Space Grotesk (display) + Inter (body)" — confirmed across light + dark iterations                                                                                                           |
| **Body font**         | Inter (400, **not 300**)                                                                         | User flagged 300 reads gauzy; bumping to 400 restored legibility on light backgrounds                                                                                                         |
| **Mono font**         | JetBrains Mono (400/500)                                                                         | Used for eyebrow labels, citations, data values                                                                                                                                               |
| **Avoid**             | Roboto, Arial, system-default sans, Cormorant, any serif italic                                  | "avoid generic sans like Roboto/Arial; avoid Cormorant/serif italics for emphasis"                                                                                                            |
| **Body-size minimum** | desktop max ≥ `1.4rem` (~22px), min `1.1rem`. Body weight `400`                                  | _"the main content text is too small. please make it more legible"_ → _"the text is still too small - i would like it to fill more of the slide instead of leaving extra space on the slide"_ |
| **Emphasis**          | `<em>` is solid `--accent` + weight 600. **No italic.**                                          | Sans italics don't carry editorial flourish; emphasis carried by color + weight                                                                                                               |
| **Inline assets**     | SVG inline (no CDN images for icons/charts). Decorative strokes use `stroke="currentColor"`      | "Inline SVG over CDN images so decks are self-contained"                                                                                                                                      |
| **Slide arc length**  | 10 slides default; mirrors source paper's structure                                              | "10-slide arc that mirrors the source paper's own structure (e.g., its graphical abstract)"                                                                                                   |
| **Minimal chrome**    | NO slide-number corner badges, NO keyboard-hint footer, NO orbs/grain, NO decorative backgrounds | The user iteratively removed every decorative layer that competed with content. Right-edge nav dots + top progress bar are sufficient navigation cues.                                        |
| **Padding symmetry**  | `.slide-content` uses symmetric `var(--slide-padding)` — no asymmetric top/bottom bands          | Adding top-padding to clear a slide-frame was the wrong fix; removing the slide-frame was right                                                                                               |

## Palette modes

Two confirmed modes. The palette is **NOT** locked across decks — the user has redirected between light and dark and back. When starting a new deck, ask which mode they want unless they've just specified one.

### Light Clinical

```css
:root {
  /* Surfaces */
  --bg-primary: #fafafa;
  --bg-elevated: #ffffff;
  --bg-surface: #f1f5f9;
  --line: rgba(15, 23, 42, 0.08);
  --line-strong: rgba(15, 23, 42, 0.16);

  /* Text */
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;

  /* Accent — single deep blue (legacy aliases all map here) */
  --accent: #2563eb;
  --accent-strong: #1e40af;
  --accent-soft: rgba(37, 99, 235, 0.15);
}
```

Use when: clinical, regulatory, scientific-print mood. The MARP companion deck for the same paper used this palette.

### Dark Minimal

```css
:root {
  /* Surfaces */
  --bg-primary: #0a0a0a;
  --bg-elevated: #141414;
  --bg-surface: #1c1c1c;
  --line: rgba(255, 255, 255, 0.08);
  --line-strong: rgba(255, 255, 255, 0.16);

  /* Text */
  --text-primary: #ffffff;
  --text-secondary: #b8b8b8;
  --text-muted: #6a6a6a;

  /* Accent — vivid red */
  --accent: #ef4444;
  --accent-strong: #dc2626;
  --accent-soft: rgba(239, 68, 68, 0.15);
}
```

Use when: bold, editorial, presentation-stage mood. Trigger quote: _"change the styling to a dark background with lighter text"_ with reference image showing solid black + white text + red accent.

## Shared CSS variables (palette-mode-independent)

These tokens stay constant regardless of palette. Only the surface/text/accent variables above flip between modes.

```css
:root {
  /* Legacy variable aliases — keep these so reskinning between palettes
     is one variable change. Each one was used dozens of times across
     component rules; aliasing saved ~30 edits per reskin. */
  --accent-warm: var(--accent);
  --accent-pink: var(--accent);
  --accent-gold: var(--accent);
  --accent-leaf: var(--accent);

  /* Typography */
  --font-display: "Space Grotesk", system-ui, sans-serif;
  --font-body: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", "Menlo", monospace;

  --title-size: clamp(2.4rem, 7vw, 6rem);
  --h2-size: clamp(1.9rem, 4.5vw, 3.6rem);
  --h3-size: clamp(1.25rem, 2.6vw, 1.9rem);
  --body-size: clamp(1.1rem, 1.7vw, 1.4rem);
  --small-size: clamp(0.95rem, 1.35vw, 1.2rem);
  --eyebrow-size: clamp(0.78rem, 1vw, 0.95rem);

  /* Spacing */
  --slide-padding: clamp(1.5rem, 4vw, 4rem);
  --content-gap: clamp(0.85rem, 2.2vw, 2.4rem);
  --element-gap: clamp(0.5rem, 1.1vw, 1.1rem);

  /* Motion */
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --duration-slow: 1s;
  --duration-norm: 0.7s;
}
```

## Component anchors (DO NOT hardcode in components)

When writing component CSS rules (`.card`, `.row`, `.t-title`, `.stat-num`, etc.), **always** reference these tokens. Hardcoding `clamp(0.95rem, 1.7vw, 1.25rem)` inside `.card h3` was the source of the "extra space" drift the user caught — the hardcoded value was smaller than `--h3-size`, so cards looked sparse while the rest of the deck looked dense.

**Component → token mapping** (canonical):

| Component / element                  | Property      | Token                                                                     |
| ------------------------------------ | ------------- | ------------------------------------------------------------------------- |
| Eyebrow / section label              | `font-size`   | `var(--eyebrow-size)`                                                     |
| Eyebrow / section label              | `color`       | `var(--accent)`                                                           |
| `<h2>`                               | `font-size`   | `var(--h2-size)`                                                          |
| `<h2>`                               | `font-weight` | `600`                                                                     |
| `.card h3`, `.row-title`, `.t-title` | `font-size`   | `var(--h3-size)`                                                          |
| `.card p`, `.row-desc`, `.t-desc`    | `font-size`   | `var(--body-size)`                                                        |
| `.cite`, `.row-cite`                 | `font-size`   | `clamp(0.78rem, 1vw, 0.95rem)` (mono, slightly smaller than --small-size) |
| `<em>` (anywhere)                    | `font-style`  | `normal`                                                                  |
| `<em>` (anywhere)                    | `color`       | `var(--accent)`                                                           |
| `<em>` (anywhere)                    | `font-weight` | `600`                                                                     |

## Reskinning rule (THE alias pattern)

When changing the brand's palette mode (light → dark, dark → light, or to a future third mode), edit the surface/text/accent variables in `:root` only. The legacy aliases (`--accent-warm`, `--accent-pink`, `--accent-gold`, `--accent-leaf`) automatically follow because they reference `var(--accent)`.

**Do NOT** search-and-replace component rules to use `--accent` directly. The aliases are working as intended — they let dozens of historic rules keep their semantic names while resolving to one canonical value.

## SVG icon convention

Decorative icons use `stroke="currentColor"` and let a parent set `color: var(--accent)`. Do not hardcode hex values in `stroke` attributes.

```html
<!-- Good: retints automatically on theme swap -->
<div class="row-icon" style="color: var(--accent)">
  <svg
    width="22"
    height="22"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.4"
  >
    <circle cx="12" cy="8" r="4" />
    <path d="M5 22a7 7 0 0 1 14 0" />
  </svg>
</div>

<!-- Bad: stuck on a single palette mode -->
<svg stroke="#ef4444" ...>...</svg>
```

## Things explicitly removed (don't bring them back)

These were tried and rejected during the iteration:

- **Slide-frame badges** (top-left "01" / top-right section title) — competed with the section-head eyebrow for the same coordinates. `display: none` is in the template; keep it that way.
- **Background gradient orbs** + **grain texture** — felt design-y, not clinical. Suppressed via `display: none`.
- **Bottom keyboard-hint footer** — redundant with right-edge nav dots and top progress bar.
- **Cormorant italic emphasis** — looked editorial in the original Dark Botanical theme, but the user's stated brief was "clinical / minimal." Sans italics don't carry the same flourish anyway.
- **Multiple style presets** (the upstream frontend-slides has 12) — this skill is brand-locked. Bundling 12 generic presets is "more options than the user wants." Two palette modes are the only style choice.

## When the brand might evolve

Update this file when:

- The user accepts a new palette mode (e.g., "warm sepia" for a future editorial deck) — add it as a third `:root` block under "Palette modes" with the trigger quote that established it.
- The user redirects on a token (e.g., bumps body-size again) — update the value here, then update `templates/template.html` to match.
- New durable signals emerge from at least two iterations on different decks (one data point isn't enough).

Re-running `feedback_deck_style.md` (in the user's project memory) is the longer-form audit trail. This file is the operational source.
