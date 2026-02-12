#!/usr/bin/env bash
#
# Sync user documentation from wp-motor/docs/usage to wp-docs
#
# Source:       wp-motor/docs/usage/zh  ->  docs-zh/10-user
#               wp-motor/docs/usage/en  ->  docs-en/10-user
#
# Strategy: Add new files and update existing ones. Does NOT delete
#           files that only exist in the destination.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_BASE="${1:-$SCRIPT_DIR/../wp-motor/docs/usage}"

# Resolve to absolute path
SOURCE_BASE="$(cd "$SOURCE_BASE" && pwd)"

DEST_ZH="$SCRIPT_DIR/docs-zh/10-user"
DEST_EN="$SCRIPT_DIR/docs-en/10-user"

# Validate directories exist
for dir in "$SOURCE_BASE/zh" "$SOURCE_BASE/en" "$DEST_ZH" "$DEST_EN"; do
    if [ ! -d "$dir" ]; then
        echo "ERROR: Directory not found: $dir"
        exit 1
    fi
done

echo "=== Syncing user docs ==="
echo "Source: $SOURCE_BASE"
echo ""

# --recursive  : recurse into directories
# --update     : skip files that are newer on the receiver
# --times      : preserve modification times (needed for --update to work)
# --checksum   : use checksum instead of time+size to decide whether to transfer
# --verbose    : show which files are transferred
# --itemize-changes : output a change-summary for all updates
RSYNC_OPTS=(-rtvuc --itemize-changes)

echo "--- zh -> docs-zh/10-user ---"
rsync "${RSYNC_OPTS[@]}" "$SOURCE_BASE/zh/" "$DEST_ZH/"
echo ""

echo "--- en -> docs-en/10-user ---"
rsync "${RSYNC_OPTS[@]}" "$SOURCE_BASE/en/" "$DEST_EN/"
echo ""

echo "=== Done ==="
