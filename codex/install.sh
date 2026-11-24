#!/bin/sh
# Install the model-routing role files for Codex. A plugin cannot register agents,
# so this copies codex/agents/*.toml into $CODEX_HOME/agents (default ~/.codex) and
# prints the [agents] block to add to config.toml. It never edits config.toml.
# Usage: sh codex/install.sh [--force]   (--force overwrites existing role files)
set -eu
here=$(cd "$(dirname "$0")" && pwd)
home=${CODEX_HOME:-$HOME/.codex}
mkdir -p "$home/agents"
for f in "$here"/agents/*.toml; do
  dst="$home/agents/$(basename "$f")"
  if [ -e "$dst" ] && [ "${1:-}" != "--force" ]; then
    echo "kept existing $dst (use --force to overwrite)"
  else
    cp "$f" "$dst" && echo "installed $dst"
  fi
done
if grep -q '^\[agents\]' "$home/config.toml" 2>/dev/null; then
  echo "config.toml already has [agents]; compare it with $here/agents.toml by hand."
else
  echo "Add this to $home/config.toml:"; echo; cat "$here/agents.toml"
fi
