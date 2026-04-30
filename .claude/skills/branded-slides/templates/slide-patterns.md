# slide-patterns.md

Canonical layouts for `branded-slides`. Each pattern includes an HTML snippet, when to use it, and the **content-density tier** that drives image-role mapping in `scripts/generate_images.sh`:

| Tier   | Element count | Default image role | Why                                                                |
| ------ | ------------- | ------------------ | ------------------------------------------------------------------ |
| Sparse | 0–2           | `background`       | Lots of negative space; benefits most from a hero image            |
| Medium | 3–6           | `contextual`       | Tolerates a 40%-width side image without crowding                  |
| Dense  | 7+            | `none`             | Cards/rows already fill the viewport; an image makes it unreadable |

Element count = `<section>`'s descendant `.card`, `.row`, `<h3>`, `.t-item` (timeline items).

All snippets use brand tokens from `BRAND.md`. **Never hardcode** `clamp(...)` values inside component rules — use `var(--h3-size)`, `var(--body-size)`, etc. so future bumps propagate.

Wrap each snippet in `<section class="slide" data-title="<short>">…</section>`. Most slides have a `<div class="slide-content">…</div>` inner wrapper that handles the symmetric padding.

---

## Title slide

**When:** Slide 1, every deck. Sets the tone.
**Density tier:** Sparse → image role **background**.

```html
<section class="slide title-slide" data-title="Title"
         data-image-prompt="abstract editorial illustration of <topic>, minimal, photographic">
  <div class="slide-content">
    <span class="eyebrow reveal stagger" style="--i:0;">Review · <Domain></span>
    <h1 class="reveal stagger" style="--i:1;">
      The Title<br/>of the <em>Deck</em>
    </h1>
    <p class="subtitle reveal stagger" style="--i:2;">
      One-line subtitle that does not exceed two lines.
    </p>
    <dl class="title-meta reveal stagger" style="--i:3;">
      <div><dt>Authors</dt><dd>First Last et al.</dd></div>
      <div><dt>Source</dt><dd>Journal · Year</dd></div>
      <div><dt>DOI</dt><dd>10.xxxx/yyyy</dd></div>
    </dl>
  </div>
</section>
```

Notes: `<em>` highlights one word in the title in the accent color (no italic).

---

## Three-up cards

**When:** Three parallel ideas. Most common content slide.
**Density tier:** Medium (3 cards) → image role **contextual**.

```html
<section
  class="slide"
  data-title="Three forces"
  data-image-prompt="abstract triptych illustrating <topic>, three-panel composition, monochrome accent"
>
  <div class="slide-content">
    <div class="section-head">
      <span class="eyebrow reveal stagger" style="--i:0;">Eyebrow</span>
      <h2 class="reveal stagger" style="--i:1;">
        Headline with <em>emphasis</em>.
      </h2>
    </div>
    <div class="three-up">
      <div class="card reveal stagger" style="--i:2;">
        <span class="card-eyebrow">Card 01 · Label</span>
        <h3>Card title</h3>
        <p>One short paragraph. Two sentences max.</p>
      </div>
      <div class="card reveal stagger" style="--i:3;">…</div>
      <div class="card reveal stagger" style="--i:4;">…</div>
    </div>
  </div>
</section>
```

---

## Four-up grid (2×2)

**When:** Four parallel items, paired (constraints, dimensions, etc.).
**Density tier:** Medium-dense → image role **contextual** if there's room, else **none**.

```html
<section class="slide" data-title="Constraints" data-no-image>
  <div class="slide-content">
    <div class="section-head">
      <span class="eyebrow reveal stagger" style="--i:0;"
        >What still has to be solved</span
      >
      <h2 class="reveal stagger" style="--i:1;">Heading goes here.</h2>
    </div>
    <div class="four-up">
      <div class="card reveal stagger" style="--i:2;">
        <span class="card-eyebrow">Constraint 01</span>
        <h3>Title</h3>
        <p>Description sentence.</p>
      </div>
      <div class="card reveal stagger" style="--i:3;">…</div>
      <div class="card reveal stagger" style="--i:4;">…</div>
      <div class="card reveal stagger" style="--i:5;">…</div>
    </div>
  </div>
</section>
```

Use `data-no-image` if the four cards already fill the slide; the heuristic might still classify it Medium and try to add a contextual image.

---

## Row-list

**When:** 3–5 items each with an icon, title, description, and citation. Good for a "this is happening across these areas" slide.
**Density tier:** Medium → image role **contextual**.

```html
<section
  class="slide"
  data-title="Beyond the heart"
  data-image-prompt="abstract anatomical line-art across body systems, minimal, monochrome accent"
>
  <div class="slide-content">
    <div class="section-head">
      <span class="eyebrow reveal stagger" style="--i:0;">Eyebrow</span>
      <h2 class="reveal stagger" style="--i:1;">Heading.</h2>
    </div>
    <div class="row-list">
      <div class="row reveal stagger" style="--i:2;">
        <div class="row-icon">
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.4"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <!-- icon path -->
          </svg>
        </div>
        <div>
          <div class="row-title">Item title</div>
          <div class="row-desc">
            Description sentence; ideally fits on one line at desktop.
          </div>
        </div>
        <div class="row-cite">Author Year · Venue</div>
      </div>
      <!-- repeat -->
    </div>
  </div>
</section>
```

The `.row-icon` parent inherits `color: var(--accent)`; SVG strokes use `currentColor` so they retint on theme swap.

---

## Pull-quote (headline emphasis)

**When:** One key finding stated dramatically. Usually mid-deck.
**Density tier:** Sparse-medium → image role **background**.

```html
<section
  class="slide"
  data-title="Headline finding"
  data-image-prompt="dramatic editorial illustration of <topic>, large-format, single subject"
>
  <div class="slide-content">
    <div class="section-head">
      <span class="eyebrow reveal stagger" style="--i:0;"
        >Eyebrow · the headline</span
      >
    </div>
    <div class="pull-quote reveal stagger" style="--i:1;">
      Deep-learning frameworks <em>match</em> — or
      <span class="highlight">exceed</span> — board-certified pathologist
      performance in lesion identification.
    </div>
    <p class="reveal stagger small" style="--i:2;">— Author et al., Year</p>
  </div>
</section>
```

`.highlight` paints a soft accent-tinted background under the word. `<em>` is solid accent + weight 600 (no italic).

---

## Timeline (vertical milestones)

**When:** Ordered events along a date axis (regulatory milestones, project phases).
**Density tier:** Medium → image role **contextual** (small) or **none**.

```html
<section class="slide" data-title="Regulatory landscape" data-no-image>
  <div class="slide-content">
    <div class="section-head">
      <span class="eyebrow reveal stagger" style="--i:0;"
        >Guidance · Year → Year</span
      >
      <h2 class="reveal stagger" style="--i:1;">
        Regulators are <em>catching up</em>.
      </h2>
    </div>
    <div class="timeline reveal stagger" style="--i:2;">
      <div class="timeline-track"></div>
      <div class="timeline-items">
        <div class="t-item">
          <div class="t-date">Year</div>
          <div class="t-title">Milestone <em>title</em></div>
          <div class="t-desc">One-sentence description.</div>
        </div>
        <div class="t-item featured">
          <div class="t-date">Year · headline</div>
          <div class="t-title">Most-important milestone</div>
          <div class="t-desc">Why it matters.</div>
        </div>
        <!-- 2–4 t-items total -->
      </div>
    </div>
  </div>
</section>
```

`.featured` gives the milestone a filled dot vs. an outlined one.

---

## Ring / donut chart (data viz)

**When:** A single proportion is the headline (e.g., "52% of respondents").
**Density tier:** Sparse → image role **background** (or **none** if the chart already speaks).

```html
<section class="slide" data-title="Survey" data-no-image>
  <div class="slide-content">
    <div class="section-head">
      <span class="eyebrow reveal stagger" style="--i:0;"
        >Survey · context</span
      >
      <h2 class="reveal stagger" style="--i:1;">
        Where the field <em>actually stands</em>.
      </h2>
    </div>
    <div class="survey-block">
      <div class="ring reveal stagger" style="--i:2;">
        <svg viewBox="0 0 200 200" aria-hidden="true">
          <circle
            class="ring-bg"
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke-width="14"
          />
          <circle
            class="ring-fg"
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke-width="14"
          />
        </svg>
        <div class="ring-center">
          <div class="ring-num">52<em>%</em></div>
          <div class="ring-label">label fits in two lines</div>
        </div>
      </div>
      <div class="survey-meta">
        <p class="reveal stagger lede" style="--i:3;">Context paragraph.</p>
        <div class="survey-line reveal stagger" style="--i:4;">
          <span class="label">Total respondents</span
          ><span class="value">N = 89</span>
        </div>
        <div class="survey-line featured reveal stagger" style="--i:5;">
          <span class="label">Subset of interest</span
          ><span class="value">n = 46</span>
        </div>
      </div>
    </div>
  </div>
</section>
```

Ring math: `stroke-dasharray = 2π × radius`. For r=80 → `502.65`. For 52% fill, set `stroke-dashoffset` to `502.65 × (1 - 0.52) ≈ 243.29`. The animation is gated on `.slide.visible` so the ring fills as the slide enters the viewport.

**Critical:** keep the inner label short or constrain its `max-width` to ~70% of the ring container. Long labels get clipped against the stroke.

---

## Stat row (paired metrics)

**When:** Two or three numeric callouts side by side, supporting a heading above.
**Density tier:** Medium → image role **contextual**.

```html
<section
  class="slide"
  data-title="The data problem"
  data-image-prompt="abstract gradient backdrop with overlapping data shapes, minimal, single accent"
>
  <div class="slide-content">
    <div class="section-head">
      <span class="eyebrow reveal stagger" style="--i:0;">Why now</span>
      <h2 class="reveal stagger" style="--i:1;">
        Modalities and data sources are <em>outpacing</em> traditional analysis.
      </h2>
    </div>
    <div class="stat-row reveal stagger" style="--i:2;">
      <div class="stat">
        <span class="stat-num">~63<em>%</em></span>
        <span class="stat-label">of pharma · Year survey</span>
        <span class="stat-desc">brief context for the stat.</span>
      </div>
      <div class="stat">…</div>
    </div>
  </div>
</section>
```

---

## Closing slide

**When:** Slide 10. The bottom-line takeaway.
**Density tier:** Medium (3 cards + quote) → image role **contextual**.

```html
<section
  class="slide"
  data-title="Future / closing"
  data-image-prompt="forward-looking abstract horizon, minimal, accent gradient"
>
  <div class="slide-content closing">
    <div class="section-head" style="margin-bottom: 0;">
      <span class="eyebrow reveal stagger" style="--i:0;"
        >Future directions</span
      >
    </div>
    <div class="three-up">
      <div class="card reveal stagger" style="--i:1;">…</div>
      <div class="card reveal stagger" style="--i:2;">…</div>
      <div class="card reveal stagger" style="--i:3;">…</div>
    </div>
    <div class="closing-quote reveal stagger" style="--i:4;">
      The bottom-line statement is a
      <span class="accent">single emphasized phrase</span>, not a paragraph.
    </div>
    <div class="closing-attr reveal stagger" style="--i:5;">
      — Source · Year
    </div>
  </div>
</section>
```

`.closing` overrides `.slide-content` to `align-items: flex-start` for left-aligned closing layout.

---

## When to add `data-image-prompt` vs let auto-derive run

- **Set it explicitly** when the slide's heading is generic ("Future directions") and wouldn't produce a meaningful image. Override with a domain-specific prompt.
- **Skip it** when the eyebrow + h2 already encode the slide's subject — auto-derivation builds a fine prompt from those.
- **Set `data-no-image`** when the slide is already visually dense (4-up cards, full ring chart with metadata) and an image would only add noise.

## Reveal/animation indices (`--i: N`)

Each animated child sets its own stagger index. The CSS rule:

```css
.stagger {
  transition-delay: calc(var(--i, 0) * 0.08s + 0.1s);
}
```

Index from 0 in source order. The first revealed element fires at 0.1s, each subsequent one 80ms later. Keep indices monotonically increasing within a slide; gaps are fine if you want larger pauses.
