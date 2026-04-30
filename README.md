# slides

A workspace for building presentation decks via Claude Code. Two project-scoped skills; pick by output format.

## Skills

- **`.claude/skills/branded-slides/`** — self-contained HTML decks with the iterated brand baked in (Space Grotesk + Inter, two palette modes, scroll-snap nav, optional AI image generation via OpenRouter Nano Banana 2). Use when you want a presentation-ready deck that opens in any browser.
- **`.claude/skills/marp-slides/`** — Markdown source compiled to **editable** PowerPoint via pandoc, plus optional HTML via Marp CLI. Use when stakeholders need to edit the deck in PowerPoint, Keynote, or LibreOffice Impress.

The two coexist; the brand defaults are HTML-specific. See `.claude/skills/branded-slides/docs/PPTX_EXPORT.md` for the hand-off pattern.

## Getting started

Open the folder in Claude Code and ask for a deck — for example:

> Build me a 10-slide deck on X with a dark palette.

Claude routes to the right skill based on output format.

## Structure

- `.claude/skills/branded-slides/` — HTML deck skill with brand + AI images
- `.claude/skills/marp-slides/` — editable PPTX skill via pandoc
- `.planning/plans/` — implementation plans for non-trivial work
- decks live in `decks/<topic>/` subfolders (or at the repo root, your call)
