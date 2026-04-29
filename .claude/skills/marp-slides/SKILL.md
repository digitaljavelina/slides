---
name: marp-slides
description: Author beautiful Markdown-driven slide decks. Produces fully editable PowerPoint (.pptx) as the primary output and HTML as an optional secondary export. Use when the user asks to make a presentation, slide deck, talk, or "slides".
---

# marp-slides

Markdown-first slide decks with **editable PowerPoint** as the default output
and HTML as an optional export. Three themes ship out of the box; the user
selects one per deck via front-matter.

## When to use

- "Make me a deck about X"
- "Build a presentation on X"
- "Turn this outline into slides"
- Any request involving slides, decks, talks, keynote material

## How it works

```
Markdown source  ──►  Pandoc + reference.pptx  ──►  deck.pptx  (editable)
                 ╰──► Marp CLI + theme.css     ──►  deck.html  (optional)
```

The same `.md` source produces both. PowerPoint output is **native and
editable**: titles, bullets, and content are real text boxes the user can edit
in Microsoft PowerPoint, Keynote, or LibreOffice Impress.

## Themes

Three are bundled. Pick by setting `theme:` in the deck's front-matter.

| Theme              | Vibe                                                          |
|--------------------|---------------------------------------------------------------|
| `modern-minimal`   | Light, sans-serif (Inter), single blue accent. Default pick.  |
| `dark-technical`   | GitHub-dark background, JetBrains Mono titles, neon accents.  |
| `editorial-serif`  | Cream paper, Playfair Display headlines, terracotta accent.   |

Each theme has matching files at:
- `themes/<name>/reference.pptx` — pandoc styling for PPTX
- `themes/<name>/theme.css` — Marp styling for HTML

## Authoring rules (read before writing slides)

1. **Front-matter is required** — start every deck with the YAML block from
   `templates/starter.md`. Set `theme:` to one of the three theme names.
2. **`---` separates slides.** Both pandoc and Marp respect this.
3. **One H1 per slide** is the slide title. Subsequent content is the body.
4. **Slide-level directives** use HTML comments: `<!-- _class: lead -->`,
   `<!-- _class: section -->`, `<!-- _class: quote -->`. These style the slide
   for Marp HTML; pandoc ignores them (PPTX uses layout from the reference).
5. **Two columns** use pandoc fenced divs:
   ```
   ::: columns
   :::: column
   left content
   :::::
   :::: column
   right content
   :::::
   :::
   ```
   This produces native two-column layout in PPTX. (Marp's CSS handles them
   too if the active theme is one of the bundled ones.)
6. **Images** use plain `![alt text](path)`. The alt text becomes the
   caption underneath the image in PPTX, so make it real (a one-line caption
   the audience should read). Avoid Marp width hints like `![w:900](...)` —
   pandoc would print `w:900` as the visible caption.
7. **Speaker notes** go inside HTML comments. Pandoc converts them into PPTX
   notes; Marp hides them.
   ```
   <!--
   Speaker note: emphasize the trade-off here.
   -->
   ```
8. **Keep slides sparse.** One idea per slide. Trim words. Don't paste prose.

## Workflow when asked to build a deck

Follow these steps in order.

### 1. Set up a deck workspace

If the user is in a fresh repo, create a `decks/<topic>/` directory and copy
the starter:

```bash
mkdir -p decks/<topic>
cp .claude/skills/marp-slides/templates/starter.md decks/<topic>/deck.md
```

### 2. Author the content

Edit `deck.md`. Replace the starter's content with the user's topic. Keep the
front-matter; just change `title`, `author`, `theme`, etc. Use the layouts
demonstrated in the starter (lead, section, content, two-column, image, code,
table, quote, takeaway, closing). Aim for **6–12 slides** unless the user
specifies otherwise.

### 3. Build PPTX (primary output)

PPTX is the default. Always produce this.

```bash
DECK=decks/<topic>/deck.md
THEME=$(grep -m1 '^theme:' "$DECK" | awk '{print $2}' | tr -d '"')
SKILL=.claude/skills/marp-slides
pandoc "$DECK" \
  -o "${DECK%.md}.pptx" \
  --reference-doc="$SKILL/themes/$THEME/reference.pptx" \
  --slide-level=1 \
  --resource-path=".:$(dirname "$DECK"):$SKILL"
```

`--slide-level=1` tells pandoc that each `# H1` starts a new slide.
`--resource-path` lets the deck reference images from the skill's `assets/`.

### 4. Build HTML (only if asked)

HTML is opt-in. Build it only if the user requests HTML/web export.

```bash
npx --yes @marp-team/marp-cli@latest "$DECK" \
  --theme "$SKILL/themes/$THEME/theme.css" \
  --html \
  --no-config-file \
  -o "${DECK%.md}.html"
```

### 5. Tell the user

Report what was produced and where:

> Built `decks/<topic>/deck.pptx` (editable in PowerPoint, Keynote, and
> Impress). To export HTML too, say "also build the HTML."

## Selecting a theme without asking

If the user hasn't specified a theme, pick by topic:

- Engineering, infra, demos, dev-tooling → `dark-technical`
- Story-driven, narrative, brand, keynote → `editorial-serif`
- Anything else, including business and product → `modern-minimal`

State your choice in one line so the user can override it.

## Validation checklist before reporting "done"

Run through this list every time:

- [ ] Front-matter has `title`, `author`, and a valid `theme`.
- [ ] Every slide has exactly one H1.
- [ ] Pandoc command exits 0 and the `.pptx` file exists with non-zero size.
- [ ] If HTML was requested, Marp exits 0 and the `.html` file exists.
- [ ] No slide contains a wall of prose. If a slide reads like a paragraph,
      split or trim it.

## Adding a new theme

1. Add an entry to `THEMES` in `scripts/build_reference_pptx.py` with fonts
   and colors.
2. Run `python3 scripts/build_reference_pptx.py` to regenerate
   `themes/<new-theme>/reference.pptx`.
3. Hand-write `themes/<new-theme>/theme.css` mirroring the same colors and
   fonts (use one of the existing themes as a starting point).
4. Add the new theme to the table in this file.

## File map

```
.claude/skills/marp-slides/
├── SKILL.md                          # this file
├── templates/
│   └── starter.md                    # copy this to start a new deck
├── themes/
│   ├── modern-minimal/
│   │   ├── reference.pptx
│   │   └── theme.css
│   ├── dark-technical/
│   │   ├── reference.pptx
│   │   └── theme.css
│   └── editorial-serif/
│       ├── reference.pptx
│       └── theme.css
├── assets/
│   ├── images/                       # placeholder hero images
│   └── icons/                        # check, bolt, target, spark
└── scripts/
    ├── build_reference_pptx.py       # regenerate themed pandoc references
    └── build_sample_assets.py        # regenerate placeholder images
```

## Tooling requirements

The skill expects these on the host:

- `pandoc` (≥ 3.0) — PPTX rendering
- `python3` with `python-pptx` and `Pillow` — only if regenerating themes/assets
- `npx` (Node 18+) — pulls Marp CLI on demand for HTML export

If any are missing, install them and retry. Do not silently fall back to
Marp's default `--pptx` mode: it produces image-only slides that aren't
editable, which defeats the purpose of this skill.
