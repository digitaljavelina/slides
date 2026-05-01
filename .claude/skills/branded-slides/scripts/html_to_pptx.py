"""Extract a branded-slides HTML deck into intermediate Markdown for pandoc.

Reads `decks/<slug>/index.html`, walks each `<section class="slide">`, and
maps the brand's layout patterns (`.three-up`, `.row-list`, `.timeline`,
`.pull-quote`, `.four-up`, `.stat-row`, `.survey-block`, `.slide-image`,
`.slide-bg`, title-slide, closing-quote) to clean Markdown analogues.

The output is a build artefact, not a source file — pandoc consumes it
immediately and renders the final PPTX. Authors stay in the HTML.

Design choices:

  - **Stdlib only.** html.parser + pathlib + sys + tempfile. No bs4, no lxml.
  - **Bullet lists by default.** PPTX layouts are simpler than HTML; mapping
    every brand pattern to its `<ul>` analogue produces predictable, editable
    output. Two-column fenced divs are skipped intentionally — pandoc-pptx
    requires them to be the *only* content on a slide, which conflicts with
    the imagery this script also emits.
  - **`<em>` → `**bold**`.** The brand renders <em> as accent-colored weight 600,
    not italic. Pandoc Markdown italic (`*text*`) becomes PPTX italic, which the
    user has explicitly rejected. Bold is the closest plain-text emphasis.
  - **Images at end.** Both `<img class="slide-bg">` and `<aside class="slide-image">`
    become a single `![alt](path)` line after the text content. PPTX has no
    background concept; we degrade both to inline pictures.

Usage:
    python3 html_to_pptx.py <deck.html> [--out <md-path>]

Without --out, prints the Markdown to stdout (the wrapper script captures it).
"""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# HTML void elements (no closing tag needed, no children)
VOID_ELEMENTS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "source",
        "track",
        "wbr",
    }
)


class Node:
    """Lightweight DOM node — tag + attrs + children. Children are Node or str."""

    __slots__ = ("tag", "attrs", "children")

    def __init__(self, tag: str, attrs: dict[str, str] | None = None) -> None:
        self.tag = tag
        self.attrs = attrs or {}
        self.children: list[Node | str] = []

    @property
    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())

    def has_class(self, cls: str) -> bool:
        return cls in self.classes

    def text(self) -> str:
        """Concatenated text content with brand-aware inline formatting."""
        parts: list[str] = []
        for child in self.children:
            if isinstance(child, str):
                parts.append(child)
                continue
            if child.tag == "em":
                inner = child.text().strip()
                if inner:
                    parts.append(f"**{inner}**")
            elif child.tag == "br":
                parts.append("\n")
            elif child.tag in {"script", "style"}:
                continue
            else:
                parts.append(child.text())
        text = "".join(parts)
        # Collapse runs of whitespace into single spaces; preserve explicit \n
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        return text.strip()

    def find(self, tag: str | None = None, *, cls: str | None = None) -> "Node | None":
        for desc in self.descendants():
            if tag and desc.tag != tag:
                continue
            if cls and not desc.has_class(cls):
                continue
            return desc
        return None

    def find_all(
        self, tag: str | None = None, *, cls: str | None = None
    ) -> list["Node"]:
        result: list[Node] = []
        for desc in self.descendants():
            if tag and desc.tag != tag:
                continue
            if cls and not desc.has_class(cls):
                continue
            result.append(desc)
        return result

    def children_nodes(self) -> list["Node"]:
        return [c for c in self.children if isinstance(c, Node)]

    def descendants(self) -> "list[Node]":
        out: list[Node] = []
        stack: list[Node] = [self]
        while stack:
            node = stack.pop()
            if node is not self:
                out.append(node)
            stack.extend(reversed(node.children_nodes()))
        return out


class _DOMBuilder(HTMLParser):
    """Builds a Node tree from raw HTML, ignoring scripts/comments."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("__root__")
        self.stack: list[Node] = [self.root]
        self._skip_data = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attrs_dict = {k: (v or "") for k, v in attrs}
        node = Node(tag, attrs_dict)
        self.stack[-1].children.append(node)
        if tag in VOID_ELEMENTS:
            return
        self.stack.append(node)
        if tag in {"script", "style"}:
            self._skip_data += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_ELEMENTS:
            return
        # Pop matching tag (lenient — some HTML is sloppy)
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                if self.stack[i].tag in {"script", "style"}:
                    self._skip_data -= 1
                self.stack = self.stack[:i]
                return

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attrs_dict = {k: (v or "") for k, v in attrs}
        self.stack[-1].children.append(Node(tag, attrs_dict))

    def handle_data(self, data: str) -> None:
        if self._skip_data:
            return
        if data:
            self.stack[-1].children.append(data)


def parse_html(source: str) -> Node:
    builder = _DOMBuilder()
    builder.feed(source)
    builder.close()
    return builder.root


# ---------------------------------------------------------------------------
# Pattern → Markdown mappers
# ---------------------------------------------------------------------------


def _yaml_quote(value: str) -> str:
    return value.replace('"', '\\"')


def _bold(text: str) -> str:
    """Wrap in **, stripping any nested ** to avoid pandoc parser confusion.
    The brand uses <em> for solid-accent emphasis inside h3/row-title; when
    those wrappers are themselves bold in PPTX, the inner ** becomes
    redundant and produces broken nesting like '**outer **inner****'."""
    cleaned = text.replace("**", "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return f"**{cleaned}**" if cleaned else ""


def _one_line(text: str) -> str:
    """Collapse internal newlines (e.g. from <br> in h1) to single spaces.
    Slide titles must be one line; multi-line titles fragment the rendered
    PPTX into multiple paragraphs."""
    return re.sub(r"\s+", " ", text).strip()


def _frontmatter(
    title: str,
    palette: str,
    subtitle: str = "",
    author: str = "",
    date: str = "",
) -> str:
    """YAML front-matter for pandoc. Only `title` and `palette` are required;
    optional fields (subtitle/author/date) come from the HTML title-slide's
    `<p class="subtitle">` and `<dl class="title-meta">` if present."""
    lines = ["---"]
    lines.append(f'title: "{_yaml_quote(title)}"')
    if subtitle:
        lines.append(f'subtitle: "{_yaml_quote(subtitle)}"')
    if author:
        lines.append(f'author: "{_yaml_quote(author)}"')
    if date:
        lines.append(f'date: "{_yaml_quote(date)}"')
    lines.append(f"palette: {palette}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def _three_up(node: Node) -> str:
    """`.three-up > .card` → bullet list with bold h3 + body text."""
    lines: list[str] = []
    for card in node.find_all("div", cls="card"):
        h3 = card.find("h3")
        h3_md = _bold(h3.text()) if h3 else ""
        ps = card.find_all("p")
        body = _one_line(" ".join(p.text() for p in ps if p.text()))
        if h3_md and body:
            lines.append(f"- {h3_md} — {body}")
        elif h3_md:
            lines.append(f"- {h3_md}")
        elif body:
            lines.append(f"- {body}")
    return "\n".join(lines)


def _four_up(node: Node) -> str:
    """`.four-up > .card` → 2×2 pipe table (h3 in first column, body in second)."""
    rows: list[tuple[str, str]] = []
    for card in node.find_all("div", cls="card"):
        h3 = card.find("h3")
        ps = card.find_all("p")
        rows.append(
            (
                _one_line(h3.text() if h3 else ""),
                _one_line(" ".join(p.text() for p in ps if p.text())),
            )
        )
    if not rows:
        return ""
    out = ["| Decision | Trade-off |", "|---|---|"]
    for h, body in rows:
        # Table cells can't contain pipes — escape (newlines already stripped by _one_line)
        h_escaped = h.replace("|", "\\|").replace("**", "")
        body_escaped = body.replace("|", "\\|")
        out.append(f"| **{h_escaped}** | {body_escaped} |")
    return "\n".join(out)


def _row_list(node: Node) -> str:
    """`.row-list > .row` → bullet list with bold title."""
    lines: list[str] = []
    for row in node.find_all("div", cls="row"):
        title = row.find("div", cls="row-title")
        desc = row.find("div", cls="row-desc")
        title_md = _bold(title.text()) if title else ""
        desc_text = _one_line(desc.text()) if desc else ""
        if title_md and desc_text:
            lines.append(f"- {title_md} — {desc_text}")
        elif title_md:
            lines.append(f"- {title_md}")
        elif desc_text:
            lines.append(f"- {desc_text}")
    return "\n".join(lines)


def _pull_quote(node: Node) -> str:
    """`.pull-quote` → block quote."""
    text = node.text()
    if not text:
        return ""
    # Block quote each line
    return "\n".join(f"> {line}" for line in text.split("\n") if line.strip())


def _timeline(node: Node) -> str:
    """`.timeline > .t-item` → bullet list with date prefix."""
    lines: list[str] = []
    for item in node.find_all("div", cls="t-item"):
        date = item.find("div", cls="t-date")
        title = item.find("div", cls="t-title")
        desc = item.find("div", cls="t-desc")
        date_text = _one_line(date.text() if date else "")
        title_text = _one_line(title.text() if title else "")
        desc_text = _one_line(desc.text() if desc else "")
        if date_text and title_text:
            prefix = _bold(f"{date_text} · {title_text}")
        else:
            prefix = _bold(title_text or date_text)
        if desc_text:
            lines.append(f"- {prefix} — {desc_text}")
        elif prefix:
            lines.append(f"- {prefix}")
    return "\n".join(lines)


def _stat_row(node: Node) -> str:
    """`.stat-row > .stat` → bullet list, num + label/desc."""
    lines: list[str] = []
    for stat in node.find_all("div", cls="stat"):
        num = stat.find("span", cls="stat-num")
        label = stat.find("span", cls="stat-label")
        desc = stat.find("span", cls="stat-desc")
        num_md = _bold(num.text()) if num else ""
        label_text = _one_line(label.text() if label else "")
        desc_text = _one_line(desc.text() if desc else "")
        body_parts = [t for t in (label_text, desc_text) if t]
        body = " — ".join(body_parts)
        if num_md and body:
            lines.append(f"- {num_md} {body}")
        elif num_md:
            lines.append(f"- {num_md}")
        elif body:
            lines.append(f"- {body}")
    return "\n".join(lines)


def _survey_block(node: Node) -> str:
    """`.survey-block` → ring number as bold lede + survey lines as bullets."""
    ring_num = node.find("div", cls="ring-num")
    ring_label = node.find("div", cls="ring-label")
    parts: list[str] = []
    if ring_num and ring_label:
        parts.append(f"{_bold(ring_num.text())} — {_one_line(ring_label.text())}")
    elif ring_num:
        parts.append(_bold(ring_num.text()))
    lines = list(parts)
    for survey_line in node.find_all("div", cls="survey-line"):
        label = survey_line.find("span", cls="label")
        value = survey_line.find("span", cls="value")
        if label and value:
            lines.append(f"- {_one_line(label.text())}: {_bold(value.text())}")
    return "\n".join(lines)


def _section_head_h2(slide: Node) -> str | None:
    """Pull the `.section-head h2` if present — it's the slide's content lede."""
    head = slide.find("div", cls="section-head")
    if not head:
        return None
    h2 = head.find("h2")
    return _one_line(h2.text()) if h2 else None


def _slide_title(slide: Node) -> str:
    """Best-effort slide title: data-title attr → first <h1> → first <h2>."""
    title = slide.attrs.get("data-title")
    if title:
        return _one_line(title.replace("**", ""))
    h1 = slide.find("h1")
    if h1:
        return _one_line(h1.text().replace("**", ""))
    h2 = slide.find("h2")
    if h2:
        return _one_line(h2.text().replace("**", ""))
    return "Untitled"


def _title_slide_metadata(slide: Node) -> dict[str, str]:
    """Pull title/subtitle/author/date from a `<section class="title-slide">`
    so the caller can fold them into the YAML front-matter. Pandoc renders
    the auto-generated title slide using these fields, so we skip emitting
    the title-slide section as its own `# H1` slide (which would duplicate)."""
    out: dict[str, str] = {}
    h1 = slide.find("h1")
    if h1:
        # H1s in the brand often use <br> to break a tagline across lines
        # (e.g. "Title<br>Tagline<br>More"). For PPTX, only the first
        # line is the title — anything after the first <br> falls into
        # the subtitle slot if no <p class="subtitle"> claims it.
        h1_lines = [
            line.strip()
            for line in h1.text().replace("**", "").split("\n")
            if line.strip()
        ]
        if h1_lines:
            out["title"] = h1_lines[0]
            if len(h1_lines) > 1:
                out["subtitle"] = " ".join(h1_lines[1:])
    subtitle = slide.find("p", cls="subtitle")
    if subtitle:
        out["subtitle"] = _one_line(subtitle.text())
    # title-meta dt/dd pairs — promote Author and Date if present.
    meta = slide.find("dl", cls="title-meta")
    if meta:
        for div in meta.children_nodes():
            dt = div.find("dt")
            dd = div.find("dd")
            if not (dt and dd):
                continue
            key = dt.text().strip().lower()
            if key in {"author", "authors"}:
                out["author"] = _one_line(dd.text())
            elif key in {"date", "published"}:
                out["date"] = _one_line(dd.text())
    return out


def _slide_to_markdown(slide: Node) -> str:
    """Map a single <section class="slide"> to a Markdown slide.
    Title slides are handled separately — their metadata flows into the
    YAML front-matter, so this should never be called with a title-slide."""
    out: list[str] = []
    title = _slide_title(slide)
    out.append(f"# {title}")
    out.append("")

    # Section-head h2 becomes a lede paragraph (only if it's not redundant
    # with the data-title we just used)
    lede = _section_head_h2(slide)
    if lede and lede.lower() != title.lower():
        out.append(lede)
        out.append("")

    # Recognized body patterns — first match wins. Order matters: more
    # specific patterns (survey-block) before more generic ones (three-up).
    body_md: str | None = None
    for pattern_class, mapper in (
        ("survey-block", _survey_block),
        ("timeline", _timeline),
        ("pull-quote", _pull_quote),
        ("four-up", _four_up),
        ("three-up", _three_up),
        ("row-list", _row_list),
        ("stat-row", _stat_row),
    ):
        match = slide.find("div", cls=pattern_class)
        if match is None and pattern_class == "pull-quote":
            # pull-quote is a div but may be the section-head's sibling
            match = slide.find("div", cls="pull-quote")
        if match:
            body_md = mapper(match)
            break

    if body_md:
        out.append(body_md)
        out.append("")

    # Closing-quote (last section's signature line)
    closing = slide.find("div", cls="closing-quote")
    if closing:
        out.append(f"> {closing.text()}")
        out.append("")
    closing_attr = slide.find("div", cls="closing-attr")
    if closing_attr:
        out.append(f"_{closing_attr.text()}_")
        out.append("")

    # Imagery — at most one. Prefer slide-bg, fall back to slide-image.
    img_src: str | None = None
    bg = slide.find("img", cls="slide-bg")
    if bg and bg.attrs.get("src"):
        img_src = bg.attrs["src"]
    else:
        aside = slide.find("aside", cls="slide-image")
        if aside:
            inner = aside.find("img")
            if inner and inner.attrs.get("src"):
                img_src = inner.attrs["src"]

    if img_src:
        out.append(f"![]({img_src})")
        out.append("")

    return "\n".join(out).rstrip()


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------


def html_to_markdown(html: str) -> str:
    root = parse_html(html)
    body = root.find("body")
    palette = (
        body.attrs.get("data-palette", "light-clinical").strip()
        if body
        else "light-clinical"
    )
    if palette not in {"light-clinical", "dark-minimal"}:
        palette = "light-clinical"

    # Title-slide section drives the YAML front-matter (and is NOT emitted
    # as its own `# H1` slide — pandoc auto-renders the YAML title slide).
    title_meta: dict[str, str] = {}
    if body:
        title_section = body.find("section", cls="title-slide")
        if title_section:
            title_meta = _title_slide_metadata(title_section)

    # Fall back to <title> if the title-slide section didn't supply one.
    if not title_meta.get("title"):
        title_node = root.find("title")
        if title_node:
            title_meta["title"] = _one_line(title_node.text().split("·")[0])

    sections: list[str] = [
        _frontmatter(
            title=title_meta.get("title", "Deck"),
            palette=palette,
            subtitle=title_meta.get("subtitle", ""),
            author=title_meta.get("author", ""),
            date=title_meta.get("date", ""),
        )
    ]
    if body:
        for section in body.find_all("section", cls="slide"):
            if section.has_class("title-slide"):
                continue
            sections.append(_slide_to_markdown(section))

    return "\n\n".join(sections) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract a branded-slides HTML deck into pandoc-ready Markdown."
    )
    parser.add_argument("input", type=Path, help="Path to index.html")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output Markdown path (default: stdout)",
    )
    args = parser.parse_args()

    html = args.input.read_text(encoding="utf-8")
    md = html_to_markdown(html)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(md, encoding="utf-8")
    else:
        sys.stdout.write(md)

    return 0


if __name__ == "__main__":
    sys.exit(main())
