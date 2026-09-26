"""No output URL may change without a decision.

tests/fixtures/live-sitemap.txt is what the live sitemap listed when the
fixture was taken. Every one of those URLs must still produce a file, and
the sitemap may add or drop a URL only when this file says so.
"""

import re
from pathlib import Path

from conftest import read

FIXTURE = Path(__file__).parent / 'fixtures' / 'live-sitemap.txt'
SITE = 'https://rnaforecast.com'

# URLs deliberately retired since the fixture, each with its redirect at
# Cloudflare. Empty is the normal state.
RETIRED = set()

# URLs added since the fixture: new pages, new Insights. Update the fixture
# and empty this set once they are live.
ADDED = set()


def fixture_urls():
    return {line.strip() for line in read(FIXTURE).splitlines()
            if line.strip() and not line.startswith('#')}


def test_every_live_url_still_produces_a_file(site):
    for url in sorted(fixture_urls() - RETIRED):
        path = url[len(SITE):].lstrip('/')
        target = site / (path + 'index.html' if not path or path.endswith('/')
                         else path)
        assert target.is_file(), f'{url} no longer has a file: {target}'


def test_the_sitemap_changes_only_by_decision(site):
    listed = set(re.findall(r'<loc>([^<]+)</loc>', read(site / 'sitemap.xml')))
    expected = (fixture_urls() - RETIRED) | ADDED
    assert listed == expected, (
        f'added: {sorted(listed - expected)}, dropped: {sorted(expected - listed)}')
