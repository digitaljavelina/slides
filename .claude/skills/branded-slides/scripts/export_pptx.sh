#!/usr/bin/env bash
# export_pptx.sh — branded-slides editable-PowerPoint export
#
# Reads a Markdown source (one slide per `---`-separated section, with a
# `palette:` front-matter key) and renders it to .pptx via pandoc, using
# the matching themed reference.pptx for brand colors and fonts.
#
# Usage:
#   scripts/export_pptx.sh decks/<slug>/source.md
#   scripts/export_pptx.sh decks/<slug>/source.md --output decks/<slug>/deck.pptx
#
# Requires:
#   pandoc (>= 3.0)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
THEMES_DIR="$SKILL_ROOT/themes"

usage() {
  cat <<'USAGE'
Usage: export_pptx.sh <source.md> [--output <path>]

Renders a Markdown source to editable PPTX, using the brand-themed
reference.pptx selected by the front-matter `palette:` value.

Required:
  <source.md>           Markdown source file. Must contain front-matter
                        with a `palette:` key set to one of:
                          - light-clinical
                          - dark-minimal

Options:
  --output <path>       Output .pptx path. Defaults to <source>.pptx
  -h, --help            Show this message.

Authoring:
  Start a new deck by copying templates/starter.md.

Required tools:
  pandoc (>= 3.0). Install via `brew install pandoc` on macOS.
USAGE
}

if [[ $# -lt 1 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

SOURCE="$1"
shift
OUTPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output) OUTPUT="$2"; shift 2 ;;
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
The HTML deck path does not need pandoc.
MSG
  exit 2
fi

# Pull the palette value from front-matter.
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
  echo "       Add 'palette: light-clinical' or 'palette: dark-minimal' to the front-matter." >&2
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

if [[ -z "$OUTPUT" ]]; then
  OUTPUT="${SOURCE%.md}.pptx"
fi

# Resolve images relative to the source file's directory + the skill root.
SOURCE_DIR="$(cd "$(dirname "$SOURCE")" && pwd)"
RESOURCE_PATH=".:$SOURCE_DIR:$SKILL_ROOT"

echo "Rendering: $SOURCE"
echo "Palette:   $PALETTE"
echo "Output:    $OUTPUT"

pandoc "$SOURCE" \
  --output "$OUTPUT" \
  --reference-doc="$REFERENCE" \
  --slide-level=1 \
  --resource-path="$RESOURCE_PATH"

echo "Done. Open with: open '$OUTPUT'"
