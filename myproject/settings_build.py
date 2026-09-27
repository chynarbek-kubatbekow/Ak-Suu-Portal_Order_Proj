"""Collect static assets without a database, runtime bindings or production secrets."""
from .settings import *  # noqa: F403

DEBUG = False
DATABASES = {'default': {'ENGINE': 'django.db.backends.dummy'}}
if os.environ.get('CLOUDFLARE_STATIC_BUILD') == '1':
    STORAGES['staticfiles']['BACKEND'] = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    STATIC_ROOT = BASE_DIR / 'cloudflare' / '.build' / 'assets' / 'static'
