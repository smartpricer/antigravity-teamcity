#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

# Create virtual environment if it does not exist
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

# Install / update requirements
if [ -f "$REQ_FILE" ]; then
    "$VENV_DIR/bin/pip" install --disable-pip-version-check --quiet -r "$REQ_FILE"
fi

# Run prompt.py passing stdin and any command line arguments
exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/prompt.py" "$@"
