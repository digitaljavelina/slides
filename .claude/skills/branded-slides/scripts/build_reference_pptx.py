"""Build themed reference.pptx files for pandoc.

Pandoc reads `reference.pptx` for colors, fonts, and slide masters when
converting Markdown to native, editable PowerPoint. This script starts from
pandoc's bundled default reference (which has all the layout names pandoc
expects) and rewrites the OOXML theme to apply the branded-slides identity.

Run once to (re)generate the two themed references — one per palette mode.
The output `.pptx` files are the actual artifacts that ship; this script is
the recipe.

Adapted from the marp-slides skill (which had three themes); palette values
match `templates/template.html` body[data-palette="..."] selectors so the
PPTX output and HTML output stay visually consistent.

Usage:
    python3 scripts/build_reference_pptx.py

Requires:
    pandoc (>= 3.0)
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# Palette-mode themes. Major/minor fonts match templates/template.html.
# Color values are the brand palette (see BRAND.md and feedback_deck_style.md).
# accent1 is the primary brand accent; accent2-6 are pandoc-generated chart
# colors (kept tasteful but not load-bearing for the brand).
THEMES = {
    "light-clinical": {
        "fonts": {"major": "Space Grotesk", "minor": "Inter"},
        "colors": {
            "lt1": "FAFAFA",  # bg-primary
            "dk1": "0F172A",  # text-primary
            "lt2": "F1F5F9",  # bg-surface
            "dk2": "475569",  # text-secondary
            "accent1": "2563EB",  # the brand accent
            "accent2": "1E40AF",  # accent-strong
            "accent3": "0EA5E9",  # supplementary
            "accent4": "10B981",
            "accent5": "F59E0B",
            "accent6": "8B5CF6",
            "hlink": "2563EB",
            "folHlink": "1E40AF",
        },
    },
    "dark-minimal": {
        "fonts": {"major": "Space Grotesk", "minor": "Inter"},
        "colors": {
            "lt1": "0A0A0A",  # bg-primary
            "dk1": "FFFFFF",  # text-primary
            "lt2": "1C1C1C",  # bg-surface
            "dk2": "B8B8B8",  # text-secondary
            "accent1": "EF4444",  # the brand accent
            "accent2": "DC2626",  # accent-strong
            "accent3": "F97316",  # supplementary
            "accent4": "F59E0B",
            "accent5": "EAB308",
            "accent6": "84CC16",
            "hlink": "EF4444",
            "folHlink": "DC2626",
        },
    },
}


def rewrite_theme_xml(xml: str, fonts: dict[str, str], colors: dict[str, str]) -> str:
    """Patch ppt/theme/theme1.xml with new fonts and color scheme."""

    def replace_color(name: str, hex_value: str, doc: str) -> str:
        # Match <a:NAME>...</a:NAME> and replace any sysClr/srgbClr inside it
        # with our target srgbClr.
        pattern = re.compile(rf"(<a:{name}>)(.*?)(</a:{name}>)", re.DOTALL)

        def sub(m: re.Match[str]) -> str:
            return f'{m.group(1)}<a:srgbClr val="{hex_value}"/>{m.group(3)}'

        return pattern.sub(sub, doc, count=1)

    for name, hex_value in colors.items():
        xml = replace_color(name, hex_value, xml)

    # Font scheme: rewrite the Latin major/minor typefaces.
    xml = re.sub(
        r'(<a:majorFont>\s*<a:latin typeface=")[^"]*(")',
        rf'\g<1>{fonts["major"]}\g<2>',
        xml,
        count=1,
    )
    xml = re.sub(
        r'(<a:minorFont>\s*<a:latin typeface=")[^"]*(")',
        rf'\g<1>{fonts["minor"]}\g<2>',
        xml,
        count=1,
    )

    return xml


def build_theme(spec: dict, default_pptx: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()

    with (
        zipfile.ZipFile(default_pptx, "r") as src,
        zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as dst,
    ):
        for item in src.namelist():
            data = src.read(item)
            if item == "ppt/theme/theme1.xml":
                xml = data.decode("utf-8")
                xml = rewrite_theme_xml(xml, spec["fonts"], spec["colors"])
                data = xml.encode("utf-8")
            dst.writestr(item, data)
    print(f"  wrote {out_path.relative_to(out_path.parent.parent.parent)}")


def main() -> int:
    skill_root = Path(__file__).resolve().parent.parent
    work_dir = skill_root / "scripts" / ".cache"
    work_dir.mkdir(parents=True, exist_ok=True)
    default_pptx = work_dir / "pandoc-default-reference.pptx"

    print("Fetching pandoc's default reference.pptx...")
    with default_pptx.open("wb") as f:
        subprocess.run(
            ["pandoc", "--print-default-data-file", "reference.pptx"],
            check=True,
            stdout=f,
        )

    print("Building themed references:")
    for name, spec in THEMES.items():
        out = skill_root / "themes" / name / "reference.pptx"
        build_theme(spec, default_pptx, out)

    shutil.rmtree(work_dir, ignore_errors=True)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
