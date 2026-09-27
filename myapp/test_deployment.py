"""Regression checks for hosting configuration and maintenance access."""
import json
import os
import subprocess
import sys
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import SimpleTestCase, TestCase, override_settings

from myproject.media import public_image
from django.test import RequestFactory


class HostingSettingsTests(SimpleTestCase):
    def read_settings(self, **values):
        environment = os.environ.copy()
        for name in ('RENDER', 'DATABASE_URL', 'DB_BACKEND', 'SECRET_KEY', 'DEBUG', 'DJANGO_SETTINGS_MODULE'):
            environment.pop(name, None)
        environment.update({'DEBUG': '1', **values})
        code = "import myproject.settings as s; import json; print(json.dumps(s.DATABASES['default']))"
        return subprocess.run([sys.executable, '-c', code], env=environment, capture_output=True, text=True)

    def test_sqlite_is_default(self):
        result = self.read_settings()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['ENGINE'], 'django.db.backends.sqlite3')

    def test_neon_url_selects_postgres_and_preserves_tls(self):
        result = self.read_settings(DATABASE_URL='postgresql://test:p%40ss@db.example/test?sslmode=require')
        self.assertEqual(result.returncode, 0, result.stderr)
        database = json.loads(result.stdout)
        self.assertEqual(database['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(database['PASSWORD'], 'p@ss')
        self.assertEqual(database['OPTIONS']['sslmode'], 'require')
        self.assertTrue(database['DISABLE_SERVER_SIDE_CURSORS'])

    def test_conflicting_database_settings_fail(self):
        result = self.read_settings(DB_BACKEND='sqlite', DATABASE_URL='postgresql://test@db.example/test')
        self.assertNotEqual(result.returncode, 0)

    def test_production_requires_secret(self):
        self.assertNotEqual(self.read_settings(DEBUG='0').returncode, 0)

    def test_static_build_initializes_without_sqlite_or_secrets(self):
        environment = os.environ.copy()
        environment.update(DJANGO_SETTINGS_MODULE='myproject.settings_build', DEBUG='0')
        environment.pop('SECRET_KEY', None)
        code = "import sys; sys.modules['_sqlite3'] = None; import django; django.setup(); from django.conf import settings; assert settings.DATABASES['default']['ENGINE'] == 'django.db.backends.dummy'"
        result = subprocess.run([sys.executable, '-c', code], env=environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


@override_settings(ROOT_URLCONF='myproject.worker_operations')
class WorkerMaintenanceTests(TestCase):
    token = 'test-maintenance-token-with-more-than-32-characters'

    def post(self, operation, payload=None, token=None):
        return self.client.post('/' + operation + '/', data=json.dumps(payload or {}),
                                content_type='application/json',
                                HTTP_AUTHORIZATION='Bearer ' + (token or self.token))

    def test_disabled_without_token(self):
        with patch.dict(os.environ, {'DEPLOY_TOKEN': ''}):
            self.assertEqual(self.post('migrate').status_code, 404)

    def test_unauthorized_and_get_cannot_migrate(self):
        with patch.dict(os.environ, {'DEPLOY_TOKEN': self.token}), patch('myproject.worker_operations.call_command') as command:
            self.assertEqual(self.post('migrate', token='wrong').status_code, 403)
            self.assertEqual(self.client.get('/migrate/').status_code, 405)
            command.assert_not_called()

    def test_admin_creation_does_not_overwrite_existing_user(self):
        payload = {'username': 'deployment-admin', 'password': 'A-unique-Passphrase_921!'}
        with patch.dict(os.environ, {'DEPLOY_TOKEN': self.token}):
            self.assertEqual(self.post('create-admin', payload).status_code, 201)
            payload['password'] = 'Different-Passphrase_129!'
            self.assertEqual(self.post('create-admin', payload).status_code, 409)
        user = get_user_model().objects.get(username=payload['username'])
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password('A-unique-Passphrase_921!'))


class PublicMediaTests(SimpleTestCase):
    def test_worker_upload_rejects_oversized_file_instead_of_discarding_it(self):
        from django.core.exceptions import RequestDataTooBig
        from myproject.uploads import WorkerImageUploadHandler

        handler = WorkerImageUploadHandler()
        handler.handle_raw_input(None, {}, 8 * 1024 * 1024, b'boundary')
        self.assertTrue(handler.activated)
        with self.assertRaises(RequestDataTooBig):
            handler.receive_data_chunk(b'x' * (5 * 1024 * 1024 + 1), 0)

    def test_uploaded_image_is_served_in_production(self):
        with tempfile.TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory, DEBUG=False):
            name = default_storage.save('news/photo.png', ContentFile(b'public-image'))
            response = public_image(RequestFactory().get('/media/' + name), name)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b''.join(response.streaming_content), b'public-image')
            response.close()

    def test_non_image_and_parent_paths_are_not_public(self):
        from django.http import Http404
        for name in ('../settings.py', 'news/../../.env', 'news/page.html', 'other/photo.png'):
            with self.subTest(name=name), self.assertRaises(Http404):
                public_image(RequestFactory().get('/media/test'), name)


class DatabaseImageStorageTests(TestCase):
    def setUp(self):
        from myproject.image_storage import DatabaseImageStorage
        self.storage = DatabaseImageStorage()

    def test_roundtrip_unique_names_size_and_delete(self):
        data = bytes(range(256))
        first = self.storage.save('news/photo.png', ContentFile(data))
        second = self.storage.save('news/photo.png', ContentFile(b'another-image'))
        self.assertNotEqual(first, second)
        self.assertEqual(self.storage.open(first).read(), data)
        self.assertEqual(self.storage.size(first), len(data))
        self.assertEqual(self.storage.url(first), '/media/' + first)
        self.storage.delete(first)
        self.assertFalse(self.storage.exists(first))
        self.assertTrue(self.storage.exists(second))
        with self.assertRaises(FileNotFoundError):
            self.storage.open(first)

    def test_d1_row_limit_leaves_room_for_metadata(self):
        from myproject.image_storage import MAX_IMAGE_BYTES
        from myapp.models import UploadedImage
        with override_settings(MEDIA_MAX_FILE_SIZE=MAX_IMAGE_BYTES):
            name = self.storage.save('news/big.png', ContentFile(b'x' * MAX_IMAGE_BYTES))
            row = UploadedImage.objects.get(pk=name)
            self.assertLess(len(row.content_base64) + 1000, 2_000_000)
            with self.assertRaises(ValueError):
                self.storage.save('news/too-big.png', ContentFile(b'x' * (MAX_IMAGE_BYTES + 1)))
            self.assertEqual(UploadedImage.objects.count(), 1)

    def test_public_view_reads_database_image(self):
        with override_settings(STORAGES={
            'default': {'BACKEND': 'myproject.image_storage.DatabaseImageStorage'},
            'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
        }):
            name = default_storage.save('news/photo.png', ContentFile(b'from-database'))
            response = public_image(RequestFactory().get('/media/' + name), name)
            self.assertEqual(b''.join(response.streaming_content), b'from-database')
            response.close()

    @override_settings(MEDIA_MAX_FILE_SIZE=1024 * 1024)
    def test_worker_upload_uses_smaller_database_limit(self):
        from django.core.exceptions import RequestDataTooBig
        from myproject.uploads import WorkerImageUploadHandler
        handler = WorkerImageUploadHandler()
        handler.handle_raw_input(None, {}, 2 * 1024 * 1024, b'boundary')
        with self.assertRaises(RequestDataTooBig):
            handler.receive_data_chunk(b'x' * (1024 * 1024 + 1), 0)
