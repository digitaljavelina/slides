"""Build themed reference.pptx files for pandoc.

Pandoc uses the colors, fonts, and slide masters defined in `reference.pptx`
when it converts Markdown to native, editable PowerPoint. This script starts
from pandoc's bundled default reference (which has all the layout names pandoc
expects) and rewrites the OOXML theme to apply our visual identity.

Run once to (re)generate the three themed references. The output `.pptx` files
are the actual skill artifacts that ship; this script is the recipe.

Usage:
    python build_reference_pptx.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# OOXML theme color names. The slide master's <p:clrMap> aliases these to
# bg1/tx1/bg2/tx2 (default: bg1=lt1, tx1=dk1, bg2=lt2, tx2=dk2).
THEMES = {
    "modern-minimal": {
        "fonts": {"major": "Inter", "minor": "Inter"},
        "colors": {
            "lt1": "FFFFFF",  # background
            "dk1": "1A1A1A",  # primary text
            "lt2": "F5F5F5",  # secondary background
            "dk2": "525252",  # secondary text
            "accent1": "2563EB",
            "accent2": "0EA5E9",
            "accent3": "10B981",
            "accent4": "F59E0B",
            "accent5": "EF4444",
            "accent6": "8B5CF6",
            "hlink": "2563EB",
            "folHlink": "7C3AED",
        },
    },
    "dark-technical": {
        "fonts": {"major": "JetBrains Mono", "minor": "Inter"},
        "colors": {
            "lt1": "0D1117",  # dark background (mapped to bg1)
            "dk1": "E6EDF3",  # light text (mapped to tx1)
            "lt2": "161B22",
            "dk2": "8B949E",
            "accent1": "58A6FF",
            "accent2": "39D353",
            "accent3": "F778BA",
            "accent4": "D29922",
            "accent5": "FF7B72",
            "accent6": "A371F7",
            "hlink": "58A6FF",
            "folHlink": "A371F7",
        },
    },
    "editorial-serif": {
        "fonts": {"major": "Playfair Display", "minor": "Source Serif Pro"},
        "colors": {
            "lt1": "FBF7F0",
            "dk1": "2A2422",
            "lt2": "EFE7D7",
            "dk2": "6B5E54",
            "accent1": "B5651D",
            "accent2": "8C6A3F",
            "accent3": "5A7D6F",
            "accent4": "A65A4B",
            "accent5": "3E4A4A",
            "accent6": "6B4226",
            "hlink": "B5651D",
            "folHlink": "8C6A3F",
        },
    },
}


def rewrite_theme_xml(xml: str, fonts: dict[str, str], colors: dict[str, str]) -> str:
    """Patch ppt/theme/theme1.xml with new fonts and color scheme."""

    # Color scheme: replace each <a:srgbClr val="..."/> inside the matching <a:NAME>
    # element. The default reference uses sysClr for window/text on bg1/tx1; we
    # rewrite those to srgbClr so the theme drives them.
    def replace_color(name: str, hex_value: str, doc: str) -> str:
        # Match <a:NAME> ... </a:NAME> and replace any sysClr/srgbClr inside it
        # with our target srgbClr.
        pattern = re.compile(
            rf"(<a:{name}>)(.*?)(</a:{name}>)", re.DOTALL
        )

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


def build_theme(name: str, spec: dict, default_pptx: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()

    with zipfile.ZipFile(default_pptx, "r") as src, zipfile.ZipFile(
        out_path, "w", zipfile.ZIP_DEFLATED
    ) as dst:
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
        build_theme(name, spec, default_pptx, out)

    shutil.rmtree(work_dir, ignore_errors=True)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
