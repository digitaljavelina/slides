# Marp HTML-only features

The default workflow in this skill is **Markdown → pandoc → editable
`.pptx`**. That path is the right pick when stakeholders need to edit the
deck downstream. But pandoc silently drops a few authoring patterns that
Marp supports natively, so when the deliverable is HTML (or you're
presenting from a browser) you can reach for the larger Marp feature set.

This file describes that opt-in path. The reference deck lives at
`decks/marp-features-demo/deck.md` — render it with:

```bash
marp decks/marp-features-demo/deck.md \
  --html --no-config-file \
  -o decks/marp-features-demo/deck.html
```

Open the resulting HTML in any browser and use the bottom toolbar for
presenter view, full-screen, and step-through navigation.

## Features that only fire in HTML

| Feature                  | How to invoke                                             | Notes                                         |
| ------------------------ | --------------------------------------------------------- | --------------------------------------------- |
| Fragmented bullets       | Use `*` instead of `-` for list items                     | Each click reveals the next bullet            |
| Simultaneous bullets     | Use `-` for list items                                    | All bullets appear at once                    |
| `bg`-directional images  | `![bg left](path)` (or `right`, `top`, `bottom`)          | Marp-native two-column image-plus-text        |
| `fit` header             | `# <!-- fit --> BIG`                                      | Stretches the heading to slide extents        |
| Spot directives          | `<!-- _backgroundColor: ... -->` / `<!-- _color: ... -->` | Restyles only the slide they precede          |
| KaTeX / MathJax          | Front-matter `math: katex` (or `mathjax`)                 | Inline `$...$`, block `$$...$$`               |
| Highlight.js code blocks | Specify a language after the opening fence                | Triggers syntax highlighting in HTML          |
| Presenter view           | Bottom toolbar of the rendered HTML                       | Browser-only; the PPTX path has no equivalent |

## When to choose HTML over PPTX

Pick HTML when:

- You're presenting from a browser (or want presenter view in one).
- The deck relies on fragmented lists, gradient effects, or spot styling.
- The deck has math you want rendered crisply via KaTeX or MathJax.
- Nobody downstream needs to edit the slides in PowerPoint or Keynote.

Pick PPTX (the default `marp-slides` flow) when:

- Stakeholders need to open and edit the deck.
- The deck will be merged into a corporate template later.
- Static, non-interactive output is acceptable.

You can also build both from the same source — author for the lowest
common denominator and accept that fragmented lists and spot directives
quietly become non-fragmented bullets and default styling in PPTX.

## Bullet-marker pitfall (Prettier)

If the workspace has Prettier wired into a save hook, Prettier will
normalize `*` bullets to `-` bullets, which silently turns fragmented
lists into simultaneous ones. Add the deck path to `.prettierignore` at
the workspace root, or skip the formatter for the file when authoring
fragmented-list slides.

## Relationship to the default skill

This file is reference material; the canonical authoring rules in
`SKILL.md` still apply. Treat the HTML-only features as additive — they
extend the default flow rather than replace it.
