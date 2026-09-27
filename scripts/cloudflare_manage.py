"""Run one authorized D1 maintenance operation over HTTPS. No shell secrets."""
import argparse
import getpass
import json
import os
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url', help='Worker origin, e.g. https://aksuu-portal.example.workers.dev')
    parser.add_argument('operation', choices=['migrate', 'create-admin'])
    args = parser.parse_args()
    url = urlparse(args.url)
    if url.scheme != 'https' and not (url.scheme == 'http' and url.hostname in {'localhost', '127.0.0.1'}):
        parser.error('Use HTTPS, or HTTP for local Wrangler only.')
    if url.username or url.password or url.query or url.fragment or url.path not in {'', '/'}:
        parser.error('Supply only the Worker origin, without a path or credentials.')
    token = os.environ.get('DEPLOY_TOKEN') or getpass.getpass('DEPLOY_TOKEN: ')
    payload = {}
    if args.operation == 'create-admin':
        payload = {'username': input('Username: '), 'email': input('Email: '),
                   'password': getpass.getpass('New admin password: ')}
        if payload['password'] != getpass.getpass('Repeat password: '):
            parser.error('Passwords do not match.')
    request = Request(args.url.rstrip('/') + '/__ops/' + args.operation + '/',
                      data=json.dumps(payload).encode(), method='POST',
                      headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    try:
        with urlopen(request, timeout=300) as response:
            print(response.read().decode())
    except HTTPError as error:
        print(f'HTTP {error.code}: {error.read().decode()}')
        raise SystemExit(1)


if __name__ == '__main__':
    main()
