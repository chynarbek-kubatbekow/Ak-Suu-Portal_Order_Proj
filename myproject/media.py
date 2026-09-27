"""Serve the portal's public news images from disk or D1."""
from pathlib import PurePosixPath

from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from django.views.decorators.http import require_safe

IMAGE_TYPES = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.gif': 'image/gif'}


@require_safe
def public_image(request, name):
    path = PurePosixPath(name)
    if not name.startswith('news/') or '..' in path.parts or '\\' in name or path.suffix.lower() not in IMAGE_TYPES:
        raise Http404
    if not default_storage.exists(name):
        raise Http404
    try:
        response = FileResponse(default_storage.open(name, 'rb'), content_type=IMAGE_TYPES[path.suffix.lower()])
    except FileNotFoundError as exc:
        raise Http404 from exc
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cache-Control'] = 'public, max-age=3600'
    return response
