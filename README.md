# slides

A workspace for building presentation decks via Claude Code. One project-scoped skill, two output formats.

## The skill

**`.claude/skills/branded-slides/`** — produces both:

- **HTML deck** (`decks/<slug>/index.html`) with the iterated brand baked in: Space Grotesk + Inter, two palette modes (light-clinical, dark-minimal), scroll-snap nav, and optional AI image generation via OpenRouter Nano Banana 2. Open in any browser to present.
- **Editable .pptx** (`decks/<slug>/source.pptx`) rendered from a Markdown source via pandoc + a brand-themed `reference.pptx`. Hand off to stakeholders who edit in PowerPoint, Keynote, or LibreOffice Impress.

The two outputs share the brand but have separate source files. The HTML deck's rich layouts (3-up cards, animated ring charts, AI imagery) don't translate cleanly to PPTX; the dual-source design lets each format play to its strengths. See `.claude/skills/branded-slides/docs/PPTX_EXPORT.md` for the full translation table and authoring rules.

## Getting started

Open the folder in Claude Code and ask for a deck — for example:

> Build me a 10-slide deck on X with the dark palette.

Claude walks through palette and image-generation choices, drops the HTML deck under `decks/<slug>/`, and stops. If you also want the editable .pptx, ask for it; that's Phase 5 of the skill.

### Tooling

- **HTML deck path**: a modern browser. No Node/npm. AI imagery (optional) needs `OPENROUTER_API_KEY` set.
- **PPTX path**: `pandoc` ≥ 3.0 (`brew install pandoc` on macOS) and Python 3 stdlib. The branded `reference.pptx` files in `themes/` are committed; only rebuild them when the brand palette changes.

## Structure

- `.claude/skills/branded-slides/` — the skill: SKILL.md, BRAND.md, templates, scripts, docs, themes
- `.planning/plans/` — implementation plans for non-trivial work
- `decks/<slug>/` — generated decks (gitignored; bring your own)

## Repo intent

This is a clean template repo, shareable to team members. The repo holds skills, templates, scripts, and plans — not deck content. Each contributor brings their own decks; `.gitignore` keeps deck output local-only by default.
