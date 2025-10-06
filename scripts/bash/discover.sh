#!/usr/bin/env bash

set -euo pipefail

JSON_MODE=false
ARGS=()

show_help() {
    cat <<'EOF'
Usage: discover.sh [--json] <idea_description>

Create a backlog intake stub for a new idea and return its file path.
EOF
}

for arg in "$@"; do
    case "$arg" in
        --json)
            JSON_MODE=true
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            ARGS+=("$arg")
            ;;
    esac
done

IDEA_DESCRIPTION="${ARGS[*]:-}"
if [[ -z "$IDEA_DESCRIPTION" ]]; then
    echo "Error: idea description required." >&2
    show_help >&2
    exit 1
fi

find_repo_root() {
    local dir="$1"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.specify" ]] || [[ -d "$dir/.git" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
REPO_ROOT="$(find_repo_root "$SCRIPT_DIR")"
if [[ -z "$REPO_ROOT" ]]; then
    echo "Error: could not locate repository root." >&2
    exit 1
fi

BACKLOG_DIR="$REPO_ROOT/backlog"
mkdir -p "$BACKLOG_DIR"

HIGHEST=0
if [[ -d "$BACKLOG_DIR" ]]; then
    while IFS= read -r -d '' dir; do
        base="$(basename "$dir")"
        if [[ "$base" =~ ^I([0-9]{3})- ]]; then
            num="${BASH_REMATCH[1]}"
            num=$((10#$num))
            if (( num > HIGHEST )); then
                HIGHEST=$num
            fi
        fi
    done < <(find "$BACKLOG_DIR" -maxdepth 1 -mindepth 1 -type d -print0)
fi

NEXT=$((HIGHEST + 1))
IDEA_NUM=$(printf "I%03d" "$NEXT")

slugify() {
    local input="$1"
    echo "$input" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//'
}

SLUG=$(slugify "$IDEA_DESCRIPTION")
if [[ -z "$SLUG" ]]; then
    SLUG="idea"
fi

IDEA_DIR="$BACKLOG_DIR/${IDEA_NUM}-${SLUG}"
mkdir -p "$IDEA_DIR"

TEMPLATE="$REPO_ROOT/.specify/templates/intake-template.md"
INTAKE_FILE="$IDEA_DIR/intake.md"

if [[ -f "$TEMPLATE" ]]; then
    cp "$TEMPLATE" "$INTAKE_FILE"
else
    cat > "$INTAKE_FILE" <<'EOF'
# Idea Intake

## Overview
- **Idea ID:**
- **Working Title:**
- **Problem / Opportunity:**
- **Target Users / Stakeholders:**

## Goals & Outcomes
- Primary objectives
- Success metrics or signals

## Scope
- In scope
- Out of scope / deferrals

## Constraints & Assumptions
- Technical constraints
- Policy, compliance, or organisational limits

## Risks & Unknowns
- Major risks
- Open questions / research needed

## Proposed Approach (Optional)
- Initial ideas to explore

## Next Steps
- Decision / recommendation (proceed, research more, drop)
- Follow-up actions or owners

EOF
fi

if $JSON_MODE; then
    printf '{"IDEA_ID":"%s","IDEA_DIR":"%s","INTAKE_FILE":"%s"}\n' \
        "$IDEA_NUM" "$IDEA_DIR" "$INTAKE_FILE"
else
    cat <<EOF
IDEA_ID: $IDEA_NUM
IDEA_DIR: $IDEA_DIR
INTAKE_FILE: $INTAKE_FILE
EOF
fi
