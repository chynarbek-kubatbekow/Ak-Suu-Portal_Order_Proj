#!/usr/bin/env bash
# Copyright (c) 2026 Ak-Suu Portal Project Team. All rights reserved.
# Proprietary software. See LICENSE for terms.
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
DJANGO_SETTINGS_MODULE=myproject.settings_build python manage.py collectstatic --no-input
