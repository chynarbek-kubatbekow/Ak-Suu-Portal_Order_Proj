"""Small image storage compatible with D1's 2,000,000-byte row limit."""
import base64
from pathlib import PurePosixPath
from urllib.parse import quote
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

# D1 stores base64 in a row limited to 2,000,000 bytes. Native PostgreSQL
# deployments may use the larger MEDIA_MAX_FILE_SIZE configured in settings.
MAX_IMAGE_BYTES = 1024 * 1024


@deconstructible
class DatabaseImageStorage(Storage):
    @staticmethod
    def _model():
        from myapp.models import UploadedImage
        return UploadedImage

    def _open(self, name, mode='rb'):
        if mode not in {'r', 'rb'}:
            raise ValueError('Database images can only be opened for reading.')
        try:
            row = self._model().objects.only('content_base64').get(pk=name)
        except self._model().DoesNotExist as exc:
            raise FileNotFoundError(name) from exc
        return ContentFile(base64.b64decode(row.content_base64), name=name)

    def _save(self, name, content):
        from .media import IMAGE_TYPES
        path = PurePosixPath(name)
        if not name.startswith('news/') or '..' in path.parts or '\\' in name or path.suffix.lower() not in IMAGE_TYPES:
            raise SuspiciousFileOperation('Only news image uploads are supported.')
        max_bytes = settings.MEDIA_MAX_FILE_SIZE
        data = content.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError(f'Image uploads are limited to {max_bytes // (1024 * 1024)} MiB.')
        # Immutable, unguessable names avoid overwrites and stale cached photos.
        name = f'news/{uuid4().hex}{path.suffix.lower()}'
        self._model().objects.create(name=name, content_base64=base64.b64encode(data).decode('ascii'), size=len(data))
        return name

    def exists(self, name):
        return self._model().objects.filter(pk=name).exists()

    def delete(self, name):
        self._model().objects.filter(pk=name).delete()

    def size(self, name):
        try:
            return self._model().objects.values_list('size', flat=True).get(pk=name)
        except self._model().DoesNotExist as exc:
            raise FileNotFoundError(name) from exc

    def url(self, name):
        return settings.MEDIA_URL.rstrip('/') + '/' + quote(name, safe='/')
