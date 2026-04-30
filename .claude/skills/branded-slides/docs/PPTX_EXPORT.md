# PPTX export

`branded-slides` produces HTML, not PowerPoint. If the user needs an **editable** `.pptx` (real text boxes they can edit in PowerPoint, Keynote, or LibreOffice Impress), use the in-repo **`marp-slides`** skill instead — that's the path it owns.

The two skills coexist deliberately. Pick by output format:

| Need                                                             | Skill                         |
| ---------------------------------------------------------------- | ----------------------------- |
| Self-contained HTML deck with brand + scroll-snap + AI images    | `branded-slides` (this skill) |
| Editable `.pptx` for stakeholders who edit in PowerPoint/Keynote | `.claude/skills/marp-slides/` |

## Hand-off pattern

When the user asks for an editable PowerPoint output:

1. Don't try to convert this skill's HTML to PPTX. Marp's `--pptx` mode produces image-only slides (each slide is a rasterized PNG embedded in PPTX) — that's not editable text and defeats the purpose. The exemplar deck the user pointed to (the NotebookLM-generated PPTX in iCloud Downloads) is exactly this kind of "PPTX wrapping images" — looks like a deck, can't be edited.
2. Direct the user to the `marp-slides` skill. Its workflow:

```bash
# In a fresh deck workspace
DECK=decks/<topic>/deck.md
THEME=$(grep -m1 '^theme:' "$DECK" | awk '{print $2}' | tr -d '"')
SKILL=.claude/skills/marp-slides
pandoc "$DECK" \
  -o "${DECK%.md}.pptx" \
  --reference-doc="$SKILL/themes/$THEME/reference.pptx" \
  --slide-level=1 \
  --resource-path=".:$(dirname "$DECK"):$SKILL"
```

The `marp-slides` skill ships three pandoc reference themes:

| Theme             | Best for                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------- |
| `modern-minimal`  | Closest to the Light Clinical brand mode of `branded-slides` (Inter + blue accent on white) |
| `dark-technical`  | Closest to the Dark Minimal brand mode (dark bg + accent) — not exact, palette differs      |
| `editorial-serif` | Different aesthetic; pick only if user asks for editorial/serif feel                        |

3. Don't promise visual parity. PPTX can't render scroll-snap, the reveal-on-enter animations, or the SVG-driven ring/donut charts the way HTML can. Some patterns degrade:

| Pattern in this skill                 | What happens in PPTX                                                                     |
| ------------------------------------- | ---------------------------------------------------------------------------------------- |
| Scroll-snap navigation                | Becomes click-through slides                                                             |
| Reveal-on-enter `.stagger` animations | Gone — content shows on slide entry                                                      |
| Animated SVG ring/donut               | Becomes a static donut shape                                                             |
| Hover row highlights                  | Gone                                                                                     |
| AI-generated `.slide-bg` images       | Can be embedded as full-bleed pictures, but text must be re-typed in editable text boxes |

4. If the user wants both — branded HTML for presenting, editable PPTX for sharing — author the deck in `marp-slides` first (which uses Markdown), then optionally re-render to HTML via Marp CLI. That's a one-source-two-output pattern. The brand of `branded-slides` is HTML-specific; recreating it 1:1 in PPTX would require duplicating decisions in the marp-slides themes, which is out of scope for this skill.

## Why we don't auto-convert

If a future iteration of `branded-slides` adds a "now give me PPTX too" button, it would mean:

- Importing pandoc + python-pptx + Pillow as runtime deps (this skill currently has none of those).
- Hand-mapping every CSS layout pattern to a PPTX slide layout.
- Maintaining theme parity in two formats — every time the brand evolves, two files change.

Cleaner to let `marp-slides` own that path and keep this skill HTML-pure.
