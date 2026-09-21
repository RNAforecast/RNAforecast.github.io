"""The build produces what it should, and the smoke checker agrees."""

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


def test_no_page_ships_its_own_javascript(site):
    """JSON-LD is the only script the site emits, in any build."""
    for page in sorted(site.rglob('*.html')):
        problems = []
        check_build.check_page(str(site), str(page), problems)
        script_problems = [p for p in problems if 'inline <script>' in p]
        assert script_problems == [], script_problems


def test_production_build_uses_absolute_urls(site):
    assert 'href="https://rnaforecast.com/css/rnaf.css"' in read(site / 'index.html')
