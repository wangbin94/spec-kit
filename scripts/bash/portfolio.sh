#!/usr/bin/env bash

set -euo pipefail

JSON_MODE=false
NO_WRITE=false

show_help() {
    cat <<'EOF'
Usage: portfolio.sh [OPTIONS]

Summarise Spec Kit features and update .specify/state/features.yaml.

Options:
  --json       Output JSON instead of a table
  --no-write   Skip writing the registry file (diagnostic only)
  --help       Show this help message
EOF
}

for arg in "$@"; do
    case "$arg" in
        --json)
            JSON_MODE=true
            ;;
        --no-write)
            NO_WRITE=true
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $arg" >&2
            show_help >&2
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/../portfolio.py"

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Error: portfolio.py not found at $PYTHON_SCRIPT" >&2
    exit 1
fi

PYTHON_BIN="${PYTHON:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Error: python3 is required to run the portfolio summary" >&2
    exit 1
fi

CMD=("$PYTHON_BIN" "$PYTHON_SCRIPT")
"$JSON_MODE" && CMD+=("--json")
"$NO_WRITE" && CMD+=("--no-write")

exec "${CMD[@]}"
