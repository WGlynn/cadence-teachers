#!/usr/bin/env bash
# One-command setup: clone Cadence at the pinned commit, install it, run the smoke test.
# Works in bash on Linux/macOS and Git Bash on Windows. Needs git and Python >= 3.11.
set -euo pipefail
cd "$(dirname "$0")"
CADENCE_COMMIT="${CADENCE_COMMIT:-19bee92}"   # v0.80.0+, the version most recent experiments ran on
PY="${PYTHON:-python}"
if [ ! -d vendor/cadence/.git ]; then
  git clone https://github.com/muellerberndt/cadence vendor/cadence
fi
git -C vendor/cadence fetch -q origin
git -C vendor/cadence checkout -q "$CADENCE_COMMIT"
"$PY" -m pip install -q -r requirements.txt
"$PY" -m pip install -q -e vendor/cadence
"$PY" exp/smoke_test.py
