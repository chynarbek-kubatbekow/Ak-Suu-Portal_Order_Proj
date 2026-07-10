#!/usr/bin/env bash
# Copyright (c) 2026 Ak-Suu Portal Project Team. All rights reserved.
# Proprietary software. See LICENSE for terms.
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
