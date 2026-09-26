"""The build produces what it should, and the smoke checker agrees."""

import re

import pytest

from scripts import check_build

from conftest import read

PAGES = ['index.html', 'research/index.html', 'publications/index.html',
         'insights/index.html', 'about/index.html', 'impressum/index.html',
         'datenschutz/index.html', 'thanks/index.html',
         '404.html']


def insights(site):
    """The published Insights, however many there happen to be."""
    return sorted(p for p in site.glob('insights/*/index.html'))


def test_checker_passes_on_a_real_build(site):
    problems, pages = check_build.check(str(site))
    assert problems == [], '\n'.join(problems)
    assert pages == len(PAGES) + len(insights(site))


def test_the_build_contains_nothing_unexpected(site):
    """Every page is either a known page or an Insight — no stray archive,
    tag or category listing crept back in with the article generator."""
    built = {str(p.relative_to(site)) for p in site.rglob('*.html')}
    assert built == set(PAGES) | {str(p.relative_to(site)) for p in insights(site)}


@pytest.mark.parametrize('rel', check_build.REQUIRED)
def test_required_files_exist(site, rel):
    assert (site / rel).is_file()


@pytest.mark.parametrize('rel', PAGES)
def test_pages_are_whole(site, rel):
    html = read(site / rel)
    assert html.startswith('<!DOCTYPE html>')
    assert '</html>' in html
    assert '<h1>' in html


def test_cname_is_the_custom_domain(site):
    assert read(site / 'CNAME').strip() == 'rnaforecast.com'


def test_the_retired_contact_page_is_gone(site):
    assert not (site / 'contact').exists()


def test_no_page_ships_script_beyond_json_ld_and_the_consent_gate(site):
    """The consent script is the one piece of JavaScript, and it is the same
    block on every page; anything else is script that crept in."""
    for page in sorted(site.rglob('*.html')):
        problems = []
        check_build.check_page(str(site), str(page), problems)
        script_problems = [p for p in problems if 'inline <script>' in p]
        assert script_problems == [], script_problems
        assert "var KEY='rnaf-consent'" in read(page), page


def test_a_development_build_carries_no_script_and_no_dialog(repo, tmp_path):
    """GOOGLE_ANALYTICS is set in publishconf.py only, so a local preview
    sets nothing on the device and shows no dialog."""
    import subprocess
    import sys
    out = tmp_path / 'dev'
    result = subprocess.run(
        [sys.executable, '-m', 'pelican', 'content', '-o', str(out),
         '-s', 'pelicanconf.py', '--fatal', 'warnings'],
        cwd=repo, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    for page in sorted(out.rglob('*.html')):
        html = read(page)
        # The privacy notice names the storage key in prose; the script and
        # the dialog are what must be absent.
        assert "var KEY='rnaf-consent'" not in html, page
        assert 'id="cookie-settings"' not in html, page
        assert 'googletagmanager' not in html, page


def test_production_build_uses_absolute_urls(site):
    assert re.search(r'href="https://rnaforecast\.com/css/rnaf\.css(\?v=\w+)?"',
                     read(site / 'index.html'))


def test_the_stylesheet_url_carries_its_own_fingerprint(site, repo):
    """Cloudflare caches the CSS for hours at the edge.

    Without a digest in the URL, a deploy ships new HTML against the
    previous stylesheet and the site renders unstyled until that cache
    expires — which is what happened the first time Insights went live.
    """
    import hashlib
    digest = hashlib.sha256(
        (repo / 'content' / 'css' / 'rnaf.css').read_bytes()).hexdigest()[:10]

    for page in sorted(site.rglob('*.html')):
        html = read(page)
        assert f'/css/rnaf.css?v={digest}"' in html, page
        assert 'rnaf.css"' not in html, f'{page}: unfingerprinted stylesheet'


def test_every_image_reserves_its_space(site):
    """A missing width/height is a layout shift; RST cannot emit either, so
    the plugin measures the file and the theme carries the logo's ratio."""
    import re
    for page in sorted(site.rglob('*.html')):
        for tag in re.findall(r'<img[^>]*>', read(page)):
            assert 'width=' in tag and 'height=' in tag, f'{page}: {tag}'
