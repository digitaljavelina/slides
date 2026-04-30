# HTML-derived PPTX: single-source-of-truth refactor

**Status:** proposed (2026-04-30)
**Origin:** end-to-end test of `decks/claude-on-proxmox/` surfaced content drift between hand-authored `index.html` and hand-authored `source.md`. User suggested: _"do the reverse — render the images in the html and create a pptx from the html and rendered images."_

## Goal

One authoring source per deck (`decks/<slug>/index.html`), two outputs:

1. HTML deck (already works)
2. PPTX deck, _derived_ from the HTML deck and the images generated for it

Eliminates the separate `templates/starter.md` authoring path. Authors stay in the brand template; PPTX inherits content + imagery automatically.

## Architecture

```
decks/<slug>/index.html  ──┬──► (already) open in browser
                           │
                           └──► html_to_pptx.py --extract
                                    │
                                    ▼
                                .build/source.md  (intermediate)
                                    │
                                    ▼
                                pandoc + themes/<palette>/reference.pptx
                                    │
                                    ▼
                                decks/<slug>/source.pptx
```

The intermediate Markdown is a build artefact, not a source. Authors never edit it directly.

## The pattern extractor (`html_to_pptx.py`)

Walks the HTML using the stdlib `html.parser` (no external deps). For each `<section class="slide">`:

1. Pull `data-title` → slide title (or first `<h1>`/`<h2>` if absent)
2. Detect `data-palette` from `<body>` once → set front-matter `palette:`
3. Map each child block to a Markdown analogue:

| HTML pattern                                    | Markdown analogue                                                 |
| ----------------------------------------------- | ----------------------------------------------------------------- |
| `.three-up > .card` (eyebrow + h3 + p + cite)   | Tight 3-bullet list, h3 in bold                                   |
| `.row-list > .row` (icon + title + desc + cite) | Bullet list, title bold, cite in italics                          |
| `.timeline > .t-item` (date + title + desc)     | Bullet list, date as prefix                                       |
| `.pull-quote`                                   | `> ` block quote                                                  |
| `.four-up > .card`                              | 2×2 pipe table                                                    |
| `.stat-row > .stat` (num + label + desc)        | Bold-prefix bullets                                               |
| `.survey-block + .ring`                         | Bullet list (the ring number becomes the lede)                    |
| `aside.slide-image > img[src]`                  | `![alt](src)` after content                                       |
| `img.slide-bg[src]`                             | also `![alt](src)` (PPTX has no background; falls back to inline) |
| `[data-no-image]`                               | no image emitted                                                  |
| Plain `<p>`                                     | preserved                                                         |
| Inline `<em>`                                   | preserved (pandoc styles via reference.pptx accent)               |

4. Strip empty content (eyebrows alone don't earn a bullet)
5. Emit `# <title>` followed by the mapped content, then `---` separator

Constraints already known from this session:

- **Columns must be the slide's only content.** When the extractor sees a 2-column equivalent (e.g. a 2-card `.three-up`), it emits a `:::::: {.columns}` block and skips any surrounding prose for that slide.
- **No trailing prose after a table.** Order content so any table is last on the slide.

## Front-matter handoff

The script reads from the HTML:

- `<title>` → `title:`
- `<body data-palette>` → `palette:`
- Author/date: optional `<meta name="author">` and `<meta name="date">` tags (add to `templates/template.html` as `<!-- DECK-AUTHOR -->` and `<!-- DECK-DATE -->` placeholders)

## CLI entry point

```bash
.claude/skills/branded-slides/scripts/export_pptx.sh decks/<slug>/index.html
# instead of
.claude/skills/branded-slides/scripts/export_pptx.sh decks/<slug>/source.md
```

Detect input format by extension. The existing `--output` flag still works.

## Migration

- Keep the Markdown-source path working for legacy decks (still useful when the user wants to author a stakeholder-only deck without HTML at all).
- Delete `templates/starter.md` once HTML-derived is the documented default.
- Update `templates/starter-deck.html` to be the new authoring entry point.

## Estimated effort

- ~150 lines of Python (stdlib only — `html.parser`, `pathlib`, `re`)
- ~30 minutes of pattern testing against the AI-Safety-Pharmacology and proxmox decks
- 1 doc rewrite (`docs/PPTX_EXPORT.md`)

Total: ~2 hours of focused work.

## Why not implement now

User said _"for next time"_ — flagged as a future enhancement, not a blocker for the current consolidation. Captured here so it doesn't get lost.
