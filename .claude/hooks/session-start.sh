#!/bin/bash
# Cloud sessions only: build a Python 3.11 venv from requirements-lock.txt so
# `python -m pytest` works. The container's default Python is 3.13, where the
# pinned feedparser 6.0.10 fails to import (it needs `cgi`, removed in 3.13);
# CI runs 3.11. Local machines keep their own venv: this exits there.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

PY=$(command -v python3.11 || true)
if [ -z "$PY" ]; then
  echo "session-start: python3.11 not found; tests need 3.11 (feedparser 6.0.10 breaks on 3.13)." >&2
  exit 0
fi

# venv/ is gitignored, so the hash file inside it never reaches a commit and
# disappears with the packages it describes.
hashes=venv/.session-start.sha256
if ! sha256sum --check --status "$hashes" 2>/dev/null; then
  rm -f "$hashes"
  rm -rf venv
  "$PY" -m venv venv
  venv/bin/python -m pip install -q --disable-pip-version-check -r requirements-lock.txt pytest
  sha256sum .claude/hooks/session-start.sh requirements-lock.txt > "$hashes"
fi

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export PATH=\"$PWD/venv/bin:\$PATH\""
    # Paid search stays off unless a command opts in: the Brave key's monthly
    # cap is shared with curated-podcast-generator.
    echo "export USE_SEARCH_APIS=false"
  } >> "$CLAUDE_ENV_FILE"
fi
