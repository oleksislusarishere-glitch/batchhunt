#!/usr/bin/env bash
# One-time setup: data folder + Python venv for the scanner.
# Usage: bash scripts/setup.sh
set -euo pipefail
HOME_DIR="${BATCHHUNT_HOME:-$HOME/batchhunt-data}"
mkdir -p "$HOME_DIR"/{apps,scans}
cd "$HOME_DIR"
if command -v uv >/dev/null 2>&1; then
  [ -d .venv ] || uv venv --python 3.12 .venv
  uv pip install --python .venv/bin/python requests python-jobspy pandas pypdf
else
  [ -d .venv ] || python3 -m venv .venv
  .venv/bin/pip install -q --upgrade pip
  .venv/bin/pip install -q requests python-jobspy pandas pypdf
fi
[ -f tracker.md ] || printf '# Applications\n\n| # | Date | Company | Role (conditions) | Status | CV | Notes |\n|---|---|---|---|---|---|---|\n' > tracker.md
echo "BatchHunt data folder ready: $HOME_DIR"
