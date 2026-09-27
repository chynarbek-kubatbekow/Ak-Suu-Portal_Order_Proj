"""Exercise LOCAL Wrangler's D1, admin, database images and static assets."""
import argparse
import html
import io
import json
import os
import re
import secrets
from http.cookiejar import CookieJar
from urllib.parse import urlencode, urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8787')
    args = parser.parse_args()
    origin = args.url.rstrip('/')
    if urlparse(origin).hostname not in {'127.0.0.1', 'localhost'}:
        parser.error('This test creates data and is restricted to local Wrangler.')
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    token = os.environ['DEPLOY_TOKEN']

    def send(path, data=None, headers=None):
        response = opener.open(Request(origin + path, data=data, headers=headers or {}), timeout=60)
        body = response.read()
        return response, body

    def csrf(body):
        return html.unescape(re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', body.decode()).group(1))

    def operation(name, payload):
        return send('/__ops/' + name + '/', json.dumps(payload).encode(),
                    {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token})

    # Reapplying migrations must be harmless.
    operation('migrate', {})
    username = 'smoke-' + secrets.token_hex(5)
    password = secrets.token_urlsafe(32)
    operation('create-admin', {'username': username, 'password': password, 'email': 'smoke@example.invalid'})
    for path in ('/', '/news/', '/about/', '/admin/login/', '/static/admin/css/base.css'):
        response, body = send(path)
        assert response.status == 200 and body, path
    _, body = send('/admin/login/')
    response, body = send('/admin/login/', urlencode({'username': username, 'password': password,
                          'csrfmiddlewaretoken': csrf(body), 'next': '/admin/'}).encode(),
                          {'Content-Type': 'application/x-www-form-urlencoded', 'Referer': origin + '/admin/login/'})
    assert response.url.endswith('/admin/'), 'Admin login failed'
    _, body = send('/admin/myapp/newsitem/add/')
    title = 'Worker smoke ' + secrets.token_hex(5)
    fields = {'csrfmiddlewaretoken': csrf(body), 'title': title, 'category': 'Развитие',
              'date': '2026', 'text': 'D1 image integration check', 'image': '',
              'order': '1', 'is_published': 'on', '_save': 'Save'}
    boundary = '----aksuu' + secrets.token_hex(12)
    parts = []
    for name, value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    image = io.BytesIO()
    # A sizeable image also exercises D1 bound parameters and the row limit.
    Image.frombytes('RGB', (512, 512), os.urandom(512 * 512 * 3)).save(image, format='PNG')
    image_bytes = image.getvalue()
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="image_file"; filename="{username}.png"\r\nContent-Type: image/png\r\n\r\n'.encode() + image_bytes + b'\r\n')
    parts.append(f'--{boundary}--\r\n'.encode())
    response, body = send('/admin/myapp/newsitem/add/', b''.join(parts),
                          {'Content-Type': 'multipart/form-data; boundary=' + boundary,
                           'Referer': origin + '/admin/myapp/newsitem/add/'})
    assert response.url.endswith('/admin/myapp/newsitem/'), 'News creation failed: ' + body.decode()[-1200:]
    _, body = send('/news/')
    assert title.encode() in body, 'Saved news is not public'
    # Newly created news sorts first (order=1, most recent created_at).
    image_path = html.unescape(re.search(r'src="(/media/news/[^\"]+)"', body.decode()).group(1))
    response, downloaded = send(image_path)
    assert downloaded == image_bytes, 'D1 image upload/download differs'
    assert response.headers['Content-Type'] == 'image/png'
    print('PASS: migrations, public pages, static assets, admin login, D1 news and image upload/download (no R2).')


if __name__ == '__main__':
    main()
