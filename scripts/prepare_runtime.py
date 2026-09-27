"""Create writable directories at startup, when a persistent disk is mounted."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
from django.conf import settings

database = settings.DATABASES['default']
if database['ENGINE'] == 'django.db.backends.sqlite3':
    import sqlite3

    Path(database['NAME']).parent.mkdir(parents=True, exist_ok=True)
Path(settings.MEDIA_ROOT).mkdir(parents=True, exist_ok=True)
