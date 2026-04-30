---
marp: true
theme: uncover
class: invert
paginate: true
math: katex
title: "Marp HTML Features Demo"
author: "slides workspace"
date: "2026-04-29"
footer: "marp-features-demo · HTML-only export"
---

<!-- _class: invert lead -->

# Marp HTML features

A walkthrough of the Marp-native authoring patterns that only render in
**HTML** export — fragmented lists, `bg` images, `fit` headers, spot
directives, and KaTeX math.

slides workspace · 2026-04-29

<!--
Speaker note: this deck is the opt-in HTML-feature demo. Existing decks in
the repo use pandoc -> PPTX; this one is meant to be rendered with the Marp
CLI to HTML so the HTML-only features actually fire.
-->

---

# Why a separate HTML deck?

PPTX export through pandoc is editable, but a few Marp behaviours **only
appear in HTML**:

- Fragmented (one-at-a-time) bullets
- Gradient shadows and CSS-only effects
- Presenter view in the bottom toolbar
- Spot directives that restyle a single slide

Use this deck as a reference for the HTML-only path.

---

# Bullets that appear one at a time

Asterisk bullets become **fragmented lists** in HTML — each click reveals
the next line.

* First, set the stage
* Then, complicate the picture
* Finally, land the takeaway

(Compare to the next slide, which uses dashes.)

---

# Bullets that appear all at once

Dash bullets render simultaneously — useful when the audience needs to see
the full set before you talk.

- Premise
- Counter-premise
- Synthesis

The syntax toggle (asterisk vs dash) is the entire interaction contract.

---

![bg left](../../.claude/skills/marp-slides/assets/images/hero-warm.png)

# Image on the left, text on the right

The `bg left` directive pins the image to one side of the slide so the
right side becomes a normal text column. This is the Marp-native pattern
for image-plus-text layouts.

- No fenced divs
- No custom CSS
- Works with any of the bundled themes

---

<!-- _backgroundColor: black -->
<!-- _color: #ff3b3b -->

# <!-- fit --> BIG

A spot directive (`_backgroundColor`, `_color`) restyles **only this
slide**. Combined with a `<!-- fit -->` header, it produces an impact
slide without writing any CSS.

---

# Math, inline and block

Inline math uses single dollar signs: $E = mc^2$.

Block math uses double dollar signs and gets its own line:

$$
\hat{y} = \sigma\!\left(\sum_{i=1}^{n} w_i x_i + b\right)
$$

The `math: katex` front-matter directive enables KaTeX rendering. Swap to
`math: mathjax` if a formula needs MathJax-only features.

---

# Code with language-aware highlighting

Specifying the language after the opening fence triggers Highlight.js:

```python
def fragmented_bullets(lines: list[str]) -> str:
    """Asterisk bullets render one-at-a-time in Marp HTML output."""
    return "\n".join(f"* {line}" for line in lines)
```

```css
section.lead h1 {
  font-size: 80px;
  letter-spacing: -0.02em;
}
```

---

# Build it

From the repo root:

```bash
DECK=decks/marp-features-demo/deck.md
marp "$DECK" --html --no-config-file -o "${DECK%.md}.html"
```

Open the generated `deck.html` in any browser. Use the bottom toolbar for
presenter view, full-screen, and step-through navigation.

---

<!-- _class: invert lead -->

# That is the HTML-feature surface

Use this deck as the reference any time you need fragmented lists,
`bg`-directional images, `fit` headers, spot directives, or KaTeX math —
features that the pandoc PPTX path quietly drops.
