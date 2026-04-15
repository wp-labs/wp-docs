#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

ARGS=(
    "--config" "$SCRIPT_DIR/docs-sources.json"
    "--source" "wp-motor-usage"
    "--source" "warp-parse-use"
    "--prefer-local"
    "--generate-summary"
)

if [ "${1:-}" != "" ]; then
    ARGS+=("--local-override" "wp-motor-usage=$1")
fi

python3 "$SCRIPT_DIR/scripts/sync_docs.py" "${ARGS[@]}"
