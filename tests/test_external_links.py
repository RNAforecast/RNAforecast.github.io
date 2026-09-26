"""Outbound links of the production build resolve (opt-in: needs the network).

Run with  CHECK_EXTERNAL_LINKS=1 pytest tests/test_external_links.py -s
Hosts that answer 403/429 to non-browser clients are reported but do not fail
the test; 404/410 and connection failures do. The monthly workflow in
.github/workflows/link-check.yml runs this and keeps one issue up to date.
"""
import os
import re
import socket
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import pytest

from conftest import read

pytestmark = pytest.mark.skipif(not os.environ.get('CHECK_EXTERNAL_LINKS'),
                                reason='set CHECK_EXTERNAL_LINKS=1')
SITE_HOSTS = {'rnaforecast.com', 'www.rnaforecast.com'}
# Hosts that refuse scripted requests although the page exists: LinkedIn
# answers 999, Scopus redirects to a login gate, Bluesky is a single-page
# app. Reported as blocked rather than broken.
UNRELIABLE_HOSTS = {'bsky.app', 'www.linkedin.com', 'www.scopus.com'}
# A browser-like UA: several publishers answer 403 to anything else.
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0 Safari/537.36')


def _fetch(url):
    for method in ('HEAD', 'GET'):
        req = urllib.request.Request(url, method=method,
                                     headers={'User-Agent': UA, 'Accept': '*/*'})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.status
        except urllib.error.HTTPError as e:
            if method == 'HEAD' and e.code in (400, 403, 405, 501):
                continue
            return e.code
        except (urllib.error.URLError, socket.timeout, ConnectionError, OSError) as e:
            return f'error: {e}'
    return 'error'


def test_external_links_resolve(site):
    urls = {}
    for page in site.rglob('*.html'):
        for href in re.findall(r"""href=["']?(https?://[^"' >]+)""", read(page)):
            href = href.replace('&amp;', '&')
            if urlparse(href).netloc not in SITE_HOSTS:
                urls.setdefault(href, page.relative_to(site))
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(zip(urls, pool.map(_fetch, urls)))
    broken, blocked = [], []
    for url, status in sorted(results.items()):
        if status in (403, 429, 999) or urlparse(url).netloc in UNRELIABLE_HOSTS:
            if status != 200:
                blocked.append(f'{status} {url}')
        elif status != 200:
            broken.append(f'BROKEN {status} {url}  (on {urls[url]})')
    print(f'\nchecked {len(urls)} outbound links: {len(broken)} broken, '
          f'{len(blocked)} blocked')
    for line in blocked:
        print(f'  blocked {line}')
    for line in broken:
        print(f'  {line}')
    assert not broken, '\n'.join(broken)
