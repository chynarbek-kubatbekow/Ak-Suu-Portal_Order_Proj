#!/usr/bin/env bash
# Run from the repository root, as the Cloudflare Build command.
set -euo pipefail
python -m pip install uv==0.12.3
export UV_PYTHON_PREFERENCE=only-managed
uv run --locked --project cloudflare --python 3.13.5 python scripts/build_cloudflare.py
npm ci --prefix cloudflare
