#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
if [ ! -x .venv/bin/python ]; then
  "$PYTHON" -m venv .venv
fi
if ! .venv/bin/python -c 'import torch, transformers, PIL, safetensors' 2>/dev/null; then
  .venv/bin/python -m ensurepip --upgrade >/dev/null
  .venv/bin/python -m pip install -r requirements.txt
fi
.venv/bin/python download_model.py
exec .venv/bin/python server.py
