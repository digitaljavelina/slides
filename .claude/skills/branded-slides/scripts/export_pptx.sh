#!/usr/bin/env bash
# export_pptx.sh — branded-slides editable-PowerPoint export
#
# Two input modes, picked by file extension:
#
#   1. <deck>.html  →  the canonical authoring source (single source of
#      truth). The script extracts text+image refs via html_to_pptx.py,
#      pipes the intermediate Markdown through pandoc, and writes a PPTX
#      that inherits brand colors/fonts from themes/<palette>/reference.pptx.
#
#   2. <source>.md  →  legacy path. Hand-authored Markdown with a
#      `palette:` front-matter key. Same pandoc pipeline, no extraction.
#
# Usage:
#   scripts/export_pptx.sh decks/<slug>/index.html
#   scripts/export_pptx.sh decks/<slug>/source.md
#   scripts/export_pptx.sh <input> --output <path>
#
# Requires:
#   pandoc (>= 3.0)
#   python3 (stdlib only) — for the HTML extraction path

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
THEMES_DIR="$SKILL_ROOT/themes"
EXTRACTOR="$SCRIPT_DIR/html_to_pptx.py"

usage() {
  cat <<'USAGE'
Usage: export_pptx.sh <input> [--output <path>] [--keep-intermediate]

Renders a deck to editable PPTX with the brand theme applied.

Input modes (selected by file extension):
  <input>.html          Canonical authoring source. Extracted to Markdown
                        via html_to_pptx.py, then rendered. Recommended.
  <input>.md            Legacy hand-authored Markdown. Must contain
                        front-matter with `palette:` set to:
                          - light-clinical
                          - dark-minimal

Options:
  --output <path>       Output .pptx path. Defaults to:
                          - <input dir>/source.pptx for HTML input
                          - <input>.pptx for Markdown input
  --keep-intermediate   For HTML input, keep the extracted Markdown next
                        to the output (useful for debugging the mapping).
  -h, --help            Show this message.

Required tools:
  pandoc (>= 3.0). Install via `brew install pandoc` on macOS.
  python3 (stdlib). Required for the HTML extraction path.
USAGE
}

if [[ $# -lt 1 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

SOURCE="$1"
shift
OUTPUT=""
KEEP_INTERMEDIATE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output) OUTPUT="$2"; shift 2 ;;
    --keep-intermediate) KEEP_INTERMEDIATE=1; shift ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ ! -f "$SOURCE" ]]; then
  echo "ERROR: source not found: $SOURCE" >&2
  exit 1
fi

if ! command -v pandoc >/dev/null 2>&1; then
  cat >&2 <<'MSG'
ERROR: pandoc is not installed.

Install with:
  brew install pandoc          # macOS
  apt install pandoc           # Debian/Ubuntu

The branded-slides skill requires pandoc for the editable-PPTX export path.
The HTML deck path does not need pandoc (only the PPTX export does).
MSG
  exit 2
fi

# Capture the source's directory before any path swaps — pandoc needs it
# in --resource-path so `images/foo.png` references inside the deck resolve.
SOURCE_DIR="$(cd "$(dirname "$SOURCE")" && pwd)"
INPUT_BASENAME="$(basename "$SOURCE")"
INPUT_EXT="${INPUT_BASENAME##*.}"

# If input is HTML, extract to an intermediate Markdown file first.
INTERMEDIATE=""
EXTRACTED_FROM_HTML=0
case "$INPUT_EXT" in
  html|htm)
    EXTRACTED_FROM_HTML=1
    if ! command -v python3 >/dev/null 2>&1; then
      echo "ERROR: python3 not found — required for HTML input mode." >&2
      exit 2
    fi
    if [[ ! -f "$EXTRACTOR" ]]; then
      echo "ERROR: extractor not found at $EXTRACTOR" >&2
      exit 1
    fi
    INTERMEDIATE_DIR="$(mktemp -d)"
    INTERMEDIATE="$INTERMEDIATE_DIR/source.md"
    trap '[[ -n "$INTERMEDIATE_DIR" && -d "$INTERMEDIATE_DIR" ]] && rm -rf "$INTERMEDIATE_DIR"' EXIT
    python3 "$EXTRACTOR" "$SOURCE" --out "$INTERMEDIATE"
    SOURCE="$INTERMEDIATE"
    ;;
  md|markdown)
    : # Use as-is.
    ;;
  *)
    echo "ERROR: unsupported input extension: .$INPUT_EXT" >&2
    echo "       Expected .html or .md." >&2
    exit 1
    ;;
esac

# Pull the palette value from front-matter (works for both extracted-from-HTML
# and hand-authored Markdown sources).
PALETTE="$(awk '
  /^---[[:space:]]*$/ { fm = !fm; next }
  fm && /^palette:[[:space:]]*/ {
    gsub(/^palette:[[:space:]]*/, "")
    gsub(/[[:space:]"'\''#].*$/, "")
    print
    exit
  }
' "$SOURCE")"

if [[ -z "$PALETTE" ]]; then
  echo "ERROR: no 'palette:' value found in front-matter of $SOURCE" >&2
  if [[ $EXTRACTED_FROM_HTML -eq 1 ]]; then
    echo "       The HTML extractor reads <body data-palette=\"...\"> — make sure" >&2
    echo "       the deck's <body> has a valid data-palette attribute." >&2
  else
    echo "       Add 'palette: light-clinical' or 'palette: dark-minimal' to the front-matter." >&2
  fi
  exit 1
fi

REFERENCE="$THEMES_DIR/$PALETTE/reference.pptx"
if [[ ! -f "$REFERENCE" ]]; then
  echo "ERROR: no reference.pptx for palette '$PALETTE'" >&2
  echo "       Expected: $REFERENCE" >&2
  echo "       Available: $(ls "$THEMES_DIR" 2>/dev/null | tr '\n' ' ')" >&2
  echo "       Or rebuild with: python3 scripts/build_reference_pptx.py" >&2
  exit 1
fi

# Default output path: alongside the original input.
if [[ -z "$OUTPUT" ]]; then
  if [[ $EXTRACTED_FROM_HTML -eq 1 ]]; then
    OUTPUT="$SOURCE_DIR/source.pptx"
  else
    OUTPUT="${SOURCE%.md}.pptx"
  fi
fi

RESOURCE_PATH=".:$SOURCE_DIR:$SKILL_ROOT"

echo "Rendering: $INPUT_BASENAME"
echo "Palette:   $PALETTE"
echo "Output:    $OUTPUT"

pandoc "$SOURCE" \
  --output "$OUTPUT" \
  --reference-doc="$REFERENCE" \
  --slide-level=1 \
  --resource-path="$RESOURCE_PATH"

# If asked, copy the intermediate Markdown next to the output so it can be
# inspected/diffed.
if [[ $EXTRACTED_FROM_HTML -eq 1 && $KEEP_INTERMEDIATE -eq 1 ]]; then
  KEPT="$SOURCE_DIR/source.build.md"
  cp "$INTERMEDIATE" "$KEPT"
  echo "Kept intermediate: $KEPT"
fi

echo "Done. Open with: open '$OUTPUT'"
