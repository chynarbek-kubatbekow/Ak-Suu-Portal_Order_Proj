"""Build an allowlisted Worker bundle; never copy local databases or secrets."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'cloudflare' / '.build'
SOURCE = BUILD / 'src'


def build():
    # This directory is generated exclusively by this script.
    if BUILD.resolve() != ROOT / 'cloudflare' / '.build':
        raise RuntimeError('Unexpected build directory or symlink.')
    if BUILD.exists():
        shutil.rmtree(BUILD)
    SOURCE.mkdir(parents=True)
    for package in ('myproject', 'myapp'):
        shutil.copytree(ROOT / package, SOURCE / package,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'tests.py', 'test_*.py'))
    shutil.copytree(ROOT / 'templates', SOURCE / 'templates')
    shutil.copyfile(ROOT / 'cloudflare' / 'worker.py', SOURCE / 'worker.py')
    environment = os.environ.copy()
    environment['DJANGO_SETTINGS_MODULE'] = 'myproject.settings_build'
    environment['CLOUDFLARE_STATIC_BUILD'] = '1'
    subprocess.run([sys.executable, str(ROOT / 'manage.py'), 'collectstatic', '--noinput'],
                   env=environment, cwd=ROOT, check=True)
    print('Cloudflare bundle ready in cloudflare/.build (uses D1; no R2 required).')


if __name__ == '__main__':
    build()
