"""Bounded in-memory uploads for Workers, which have no persistent local disk."""
from django.core.exceptions import RequestDataTooBig
from django.conf import settings
from django.core.files.uploadhandler import MemoryFileUploadHandler


class WorkerImageUploadHandler(MemoryFileUploadHandler):
    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        # Do not silently discard larger files when there is no disk handler.
        self.activated = True
        self.received = 0

    def receive_data_chunk(self, raw_data, start):
        self.received += len(raw_data)
        if self.received > settings.MEDIA_MAX_FILE_SIZE:
            raise RequestDataTooBig('The image upload exceeds the configured size limit.')
        return super().receive_data_chunk(raw_data, start)
