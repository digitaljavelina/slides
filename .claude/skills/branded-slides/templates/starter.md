---
title: "Your Deck Title"
author: "Your Name"
date: "Today"
palette: light-clinical
---

<!-- ===========================================================
     Branded-slides Markdown source
     ===========================================================
     This file is the source-of-truth for the EDITABLE PPTX path.
     Render it with:

         scripts/export_pptx.sh decks/<slug>/source.md

     The script reads the `palette:` front-matter (light-clinical or
     dark-minimal) and picks the matching reference.pptx for theming.

     Notes:
     - Each `---` separates slides.
     - One H1 per slide is the slide title.
     - The HTML deck path is a separate authoring flow — see SKILL.md
       Phase 2. The two outputs share the brand but not the source.
     =========================================================== -->

# Your Deck Title

A short subtitle that sets the stage in one breath.

Your Name · Today

---

# 01 · Where we're going

Set up the arc of the deck in one sentence. The audience needs to know what
they're about to learn before you start showing them.

---

# A clear, single thought per slide

The body sits below the title. Aim for fewer words than feels comfortable; the
audience reads what you write before they hear what you say.

- One idea, stated plainly
- A supporting detail
- A consequence or implication

---

# Two columns

<!--
Pandoc's PPTX writer is strict about columns: the columns block must be
the slide's ONLY content (besides the H1 title). Prose before or after the
columns will be split into separate slides. Fold any framing into the
columns themselves. Outer fence needs MORE colons than inner.
-->

:::::: {.columns}
::: {.column}
**On the left**

State the claim, the option you're recommending, or the "before" picture.
:::

::: {.column}
**On the right**

State the contrast, the alternative, or the "after" picture. Keep both sides
roughly the same length.
:::
::::::

---

# A picture worth a thousand words

When you have one, drop it in like this — alt text becomes the caption in PPTX:

`![One-line caption.](images/your-image.png)`

Image paths resolve against the source file's directory and the skill root.

---

# A table when comparison is the point

| Approach           | Editable? | HTML deck | Effort |
| ------------------ | :-------: | :-------: | :----: |
| Render this MD     |     ✓     |     —     |  low   |
| HTML via skill     |     —     |     ✓     |  low   |
| python-pptx custom |     ✓     |     —     |  high  |

The pandoc path gets us editable PPTX without writing layout code by hand.

---

# 02 · What to do next

The second section. Use the same rhythm — sparse title slide, then content
slides that earn their density.

---

# Three things to take away

1. **Start in Markdown.** Plain text travels everywhere.
2. **Keep one idea per slide.** Density kills attention.
3. **Edit in PowerPoint when needed.** The output is fully editable.

---

# Thank you

Questions, pushback, or louder applause — all welcome.

your.name@example.com
