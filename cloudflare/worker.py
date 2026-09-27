# Copyright (c) 2026 Ak-Suu Portal Project Team. All rights reserved.
import os

from workers import WorkerEntrypoint, wsgi

os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'
# The Workers WSGI bridge runs synchronous Django on Pyodide's event loop.
# django-cf performs I/O through run_sync rather than native worker threads.
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = '1'

# Bindings are accessed inside requests, not while creating the deployment snapshot.
class Default(WorkerEntrypoint):
    async def fetch(self, request):
        from django.core.wsgi import get_wsgi_application

        if not hasattr(self, '_application'):
            self._application = get_wsgi_application()
        return await wsgi.fetch(self._application, request, self.env)
