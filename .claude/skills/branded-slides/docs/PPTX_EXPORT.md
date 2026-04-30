# PPTX export

`branded-slides` produces two formats from two source files:

| Source                    | Output                                         | When to use                                                 |
| ------------------------- | ---------------------------------------------- | ----------------------------------------------------------- |
| `decks/<slug>/index.html` | HTML deck (in-browser, scroll-snap, AI images) | Presenting in a browser, sharing a URL, full-fidelity brand |
| `decks/<slug>/source.md`  | Editable `.pptx` (real text boxes)             | Stakeholders who edit in PowerPoint/Keynote/Impress         |

The two paths share the brand (Space Grotesk + Inter, palette colors, accent) but **not** the source. Authoring is independent — the HTML deck has rich layouts (3-up cards, animated ring charts, AI-generated images) that don't translate to PPTX layouts. The PPTX path is for content that needs to be edited downstream; the HTML path is for everything else.

## Quick start: PPTX from Markdown

```bash
# Copy the starter to a deck folder
mkdir -p decks/<slug>
cp .claude/skills/branded-slides/templates/starter.md decks/<slug>/source.md

# Edit the front-matter and body in your editor of choice
# (palette: light-clinical | dark-minimal)

# Render to .pptx
.claude/skills/branded-slides/scripts/export_pptx.sh decks/<slug>/source.md
```

The script reads the `palette:` value from front-matter and picks the matching `themes/<palette>/reference.pptx` for brand colors and fonts.

## How the brand reaches PowerPoint

`themes/<palette>/reference.pptx` is the bridge. Each is a regular PowerPoint file whose `theme1.xml` has been rewritten with the brand's palette colors (`accent1` = `#2563eb` for light-clinical, `#ef4444` for dark-minimal) and Latin major/minor fonts (Space Grotesk + Inter). Pandoc reads the colors, fonts, and slide masters from the reference and applies them to the rendered deck.

To regenerate the references (e.g. after editing palettes):

```bash
python3 .claude/skills/branded-slides/scripts/build_reference_pptx.py
```

That script fetches pandoc's default reference, patches its OOXML theme block with the brand values from `THEMES`, and writes the patched files back to `themes/light-clinical/reference.pptx` and `themes/dark-minimal/reference.pptx`.

## What translates, what doesn't

| HTML brand feature                   | PPTX equivalent                                                                                                                                             |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Scroll-snap navigation               | Click-through slides                                                                                                                                        |
| `.reveal` stagger animations         | Gone — content shows on slide entry                                                                                                                         |
| Animated SVG ring chart              | Becomes a static numeric callout (use a real chart shape if needed)                                                                                         |
| Inline SVG icons via `currentColor`  | Pandoc doesn't carry SVG into PPTX cleanly — use the brand's accent color directly via emphasis or color text                                               |
| AI-generated `.slide-bg` images      | Embed as full-bleed background pictures via the standard `![alt](path.png)` Markdown                                                                        |
| `.slide-image` contextual side image | Embed as right-aligned picture via the same syntax                                                                                                          |
| Hover row highlights                 | Gone                                                                                                                                                        |
| Custom fonts (Space Grotesk, Inter)  | PowerPoint substitutes if not installed; the typeface is named in the reference theme but PowerPoint's font fallback applies on machines that don't have it |

## Authoring rules for the Markdown source

1. **Front-matter is required.** Set `palette:` to `light-clinical` or `dark-minimal`. Add `title`, `author`, `date`, optional `footer`.
2. **`---` separates slides.** One H1 per slide is the slide title.
3. **Two columns** use pandoc fenced divs. **Outer fence must have MORE colons than inner**, and the columns block must be the slide's ONLY content (besides the H1) — pandoc-pptx splits surrounding prose into separate slides. Fold framing into the columns themselves:

   ```
   :::::: {.columns}
   ::: {.column}
   left content
   :::

   ::: {.column}
   right content
   :::
   ::::::
   ```

4. **Images** use plain `![alt text](path)`. The alt text becomes the caption underneath. Paths resolve against the source's directory and the skill root.
5. **Speaker notes** go inside HTML comments — pandoc converts them to PPTX notes:
   ```
   <!--
   Speaker note: emphasize the trade-off here.
   -->
   ```
6. **Keep slides sparse.** One idea per slide. Three is the max for body bullets.

## Tooling requirements

- `pandoc` (≥ 3.0). Install via `brew install pandoc` on macOS.
- `python3` (stdlib only) — only needed to regenerate the reference.pptx files.

The HTML deck path needs neither.

## Why dual sources, not one?

It's tempting to ask: "can't we generate Markdown from the HTML deck so there's only one source?" Trying it is illuminating: the HTML uses rich layouts (`.three-up`, `.timeline`, `.ring`, etc.) that have no clean Markdown analogue. Auto-translating loses content; manual translating is faster.

The honest framing is that **the two outputs serve different audiences, so they're allowed to diverge in content too.** The PPTX deck for stakeholders is often shorter and denser-with-text-than the HTML deck (which carries information visually). Dual sources make that intentional rather than a degraded translation.
