#!/usr/bin/env bash
# generate_images.sh — branded-slides image-gen orchestrator (thin wrapper)
#
# Validates env, then delegates to inject_images.py for parsing, API calls,
# caching, and idempotent injection. Keeping the heavy lift in Python lets us
# stay stdlib-only (no jq, no curl JSON parsing in bash).
#
# Usage:
#   generate_images.sh <deck.html> [--dry-run|--limit N|--refresh|--refresh-slide ID|--inject-only|--hero-2k]
#
# Env:
#   OPENROUTER_API_KEY  required for non-dry-run

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_ORCHESTRATOR="$SCRIPT_DIR/inject_images.py"

usage() {
  cat <<'USAGE'
Usage: generate_images.sh <deck.html> [options]

Required:
  <deck.html>            Path to the deck HTML file to process.

Options:
  --dry-run              Show plan; don't call OpenRouter or write images.
  --inject-only          Don't call OpenRouter; just inject from existing cache.
  --limit N              Generate at most N new images this run (good for testing).
  --refresh              Regenerate every billable slide (ignore prompt-hash cache).
  --refresh-slide <id>   Regenerate only this slide-id (can be passed multiple times).
  --hero-2k              Use image_size=2K for the title slide (otherwise 1K).
  -h, --help             Show this message.

Env:
  OPENROUTER_API_KEY     Required for non-dry-run. Get one at
                         https://openrouter.ai/keys (the user said they have credits there).

Examples:
  scripts/generate_images.sh decks/my-talk/index.html --dry-run
  scripts/generate_images.sh decks/my-talk/index.html --limit 2
  scripts/generate_images.sh decks/my-talk/index.html
  scripts/generate_images.sh decks/my-talk/index.html --refresh-slide title
USAGE
}

if [[ $# -lt 1 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ ! -f "$PY_ORCHESTRATOR" ]]; then
  echo "ERROR: Python orchestrator not found at $PY_ORCHESTRATOR" >&2
  echo "       Reinstall the skill or check the file structure." >&2
  exit 1
fi

# First arg is the deck path; everything after passes through.
DECK="$1"
shift

if [[ ! -f "$DECK" ]]; then
  echo "ERROR: deck not found: $DECK" >&2
  exit 1
fi

# Hand off to Python. The orchestrator resolves the API key from (in order):
#   1. $OPENROUTER_API_KEY env var
#   2. $OPENROUTER_KEY env var
#   3. ~/.claude/.env (key=value lines, OPENROUTER_API_KEY or OPENROUTER_KEY)
# It prints a clear error with all three sources listed if none found.
exec python3 "$PY_ORCHESTRATOR" "$DECK" "$@"
