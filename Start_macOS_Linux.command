#!/bin/sh
set -eu
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Install Python 3.10 or newer, then run this launcher again."
  exit 1
fi
if [ ! -f .venv/bin/python ]; then
  python3 -m venv .venv
fi
if ! .venv/bin/python -c 'from PySide6.QtWidgets import QApplication' >/dev/null 2>&1; then
  echo 'First-time setup needs internet. Later launches work offline.'
  .venv/bin/python -m pip install -r requirements.txt
fi
exec .venv/bin/python app.py
