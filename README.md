# slides

A workspace for building presentation decks with [MARP](https://marp.app/) via Claude Code.

## Getting started

This repo ships a project-scoped Claude Code skill at `.claude/skills/marp-slides/`. Open the folder in Claude Code and ask for a deck — for example:

> Build me a 10-slide deck on X with a dark theme and a chart on slide 4.

The skill handles MARP markdown, theming, charts, and export.

## Structure

- `.claude/skills/marp-slides/` — project-scoped slide-building skill
- decks live at the repo root as `.md` files (or in subfolders, your call)
