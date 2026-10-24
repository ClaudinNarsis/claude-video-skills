#!/usr/bin/env bash
# Copies every skill in ./skills into ~/.claude/skills (or $1).
set -euo pipefail
dest="${1:-$HOME/.claude/skills}"
mkdir -p "$dest"
cp -R "$(dirname "$0")"/skills/* "$dest"/
echo "Installed to $dest. Restart Claude Code."
