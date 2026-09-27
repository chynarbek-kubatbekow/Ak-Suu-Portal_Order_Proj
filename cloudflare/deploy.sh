#!/usr/bin/env bash
# Run from the repository root, as the Cloudflare Deploy command.
set -euo pipefail
cd cloudflare
export UV_PYTHON_PREFERENCE=only-managed
uv run --locked --python 3.13.5 pywrangler deploy
