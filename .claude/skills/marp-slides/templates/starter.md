---
title: "Your Deck Title"
author: "Your Name"
date: "Today"
marp: true
theme: modern-minimal
paginate: true
footer: "Your Org · 2026"
---

<!-- _class: lead -->

# Your Deck Title

A short subtitle that sets the stage in one breath.

Your Name · Today

---

<!-- _class: section -->

# 01

## Where we're going

---

# A clear, single thought per slide

The body sits below the title. Aim for fewer words than feels comfortable; the
audience reads what you write before they hear what you say.

- One idea, stated plainly
- A supporting detail
- A consequence or implication

---

# Two columns

::: columns
:::: column
**On the left**

State the claim, the option you're recommending, or the "before" picture.
:::::
:::: column
**On the right**

State the contrast, the alternative, or the "after" picture. Keep both sides
roughly the same length.
:::::
:::

---

# A picture worth a thousand words

![A one-line caption that explains what the audience should notice](assets/images/hero-blue.png)

---

# Code that fits the slide

```python
def build_deck(markdown: str, theme: str) -> Path:
    """Render Markdown to an editable .pptx using the chosen theme."""
    reference = THEMES_DIR / theme / "reference.pptx"
    return pandoc(markdown, reference_doc=reference, output="deck.pptx")
```

Trim every line you can. If it doesn't fit, it doesn't belong on the slide.

---

# A table when comparison is the point

| Approach            | Editable? | HTML export | Effort |
|---------------------|:---------:|:-----------:|:------:|
| Marp `--pptx`       |     ✗     |      ✓      |  low   |
| Pandoc reference    |     ✓     |      ✓      |  low   |
| python-pptx builder |     ✓     |      —      |  high  |

Pandoc gets us editable PPTX without writing layout code by hand.

---

<!-- _class: quote -->

> The best slide is the one you don't need —
> but if you need it, make it carry its weight.

---

<!-- _class: section -->

# 02

## What to do next

---

# Three things to take away

1. **Start in Markdown.** Plain text travels everywhere.
2. **Keep one idea per slide.** Density kills attention.
3. **Edit in PowerPoint when needed.** The output is fully editable.

---

<!-- _class: lead -->

# Thank you

Questions, pushback, or louder applause — all welcome.

your.name@example.com
