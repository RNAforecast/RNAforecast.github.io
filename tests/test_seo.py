"""Everything a search engine or an AI crawler reads: metadata, robots,
sitemap, llms.txt and the structured-data graph on the real build."""

import re
import subprocess
import sys
from datetime import datetime

import pytest

from conftest import graphs_in, nodes_of, read

PAGES = ['index.html', 'research/index.html', 'publications/index.html',
         'about/index.html', 'legal/index.html']

AUTHOR_ID = 'https://rnaforecast.com/#michael-t-wolfinger'


@pytest.mark.parametrize('rel', PAGES)
def test_every_page_has_the_basics(site, rel):
    html = read(site / rel)
    assert '<link rel="canonical"' in html
    assert '<meta name="description"' in html
    assert '<meta property="og:title"' in html
    assert re.search(r'<html lang="en"', html)


@pytest.mark.parametrize('rel', PAGES)
def test_the_share_card_is_offered_wherever_it_is_promised(site, rel):
    html = read(site / rel)
    assert 'twitter:card' in html
    assert 'og:image' in html
    assert 'static/images/og-card.png' in html


def test_the_share_card_exists_at_the_expected_size(site):
    from scripts.check_build import OG_CARD, OG_CARD_SIZE, png_size
    assert png_size(site / OG_CARD) == OG_CARD_SIZE


def test_pages_that_should_not_be_indexed_say_so(site):
    for rel in ['thanks/index.html', '404.html']:
        assert 'noindex' in read(site / rel)


def test_indexable_pages_are_not_accidentally_noindexed(site):
    for rel in PAGES:
        assert 'noindex' not in read(site / rel), rel


# --- robots.txt -----------------------------------------------------------

def robots(site):
    return read(site / 'robots.txt')


def test_robots_points_at_the_sitemap(site):
    assert re.search(r'(?im)^Sitemap:\s*https://rnaforecast\.com/sitemap\.xml',
                     robots(site))


@pytest.mark.parametrize('agent', [
    'GPTBot', 'ClaudeBot', 'PerplexityBot', 'CCBot', 'Google-Extended',
    'OAI-SearchBot', 'Applebot-Extended', 'meta-externalagent',
])
def test_ai_crawlers_are_welcome(site, agent):
    assert re.search(rf'(?im)^User-agent:\s*{re.escape(agent)}\s*$', robots(site))


def test_no_crawler_is_blanket_disallowed(site):
    assert not re.search(r'(?im)^Disallow:\s*/\s*$', robots(site))


def test_the_legal_page_stays_out_of_the_index(site):
    assert re.search(r'(?im)^Disallow:\s*/legal/\s*$', robots(site))


def test_every_robots_record_excludes_the_legal_page(site):
    """A named agent group does not inherit the rules of the '*' group."""
    records = [r for r in re.split(r'\n\s*\n', robots(site))
               if re.search(r'(?im)^User-agent:', r)]
    assert len(records) >= 3
    for record in records:
        agents = re.findall(r'(?im)^User-agent:\s*(\S+)', record)
        assert re.search(r'(?im)^Disallow:\s*/legal/\s*$', record), agents


def test_llms_txt_does_not_point_at_the_legal_page(site):
    llms = read(site / 'llms.txt')
    links = re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', llms)
    assert not [u for _, u in links if '/legal/' in u]


def test_llms_txt_says_the_legal_page_is_out_of_scope(site):
    assert '/legal/ is out of scope' in read(site / 'llms.txt')


def test_the_legal_page_is_absent_from_the_sitemap(site):
    assert '/legal/' not in read(site / 'sitemap.xml')


# --- sitemap --------------------------------------------------------------

def test_sitemap_lists_the_public_pages(site):
    sitemap = read(site / 'sitemap.xml')
    locs = set(re.findall(r'<loc>([^<]+)</loc>', sitemap))
    assert locs == {
        'https://rnaforecast.com/',
        'https://rnaforecast.com/about/',
        'https://rnaforecast.com/publications/',
        'https://rnaforecast.com/research/',
    }


def test_sitemap_carries_no_noise_fields(site):
    sitemap = read(site / 'sitemap.xml')
    assert '<changefreq>' not in sitemap
    assert '<priority>' not in sitemap


def test_lastmod_is_a_valid_w3c_datetime(site):
    stamps = re.findall(r'<lastmod>([^<]+)</lastmod>', read(site / 'sitemap.xml'))
    assert len(stamps) > 1
    for stamp in stamps:
        assert re.fullmatch(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}', stamp), stamp


def test_lastmod_comes_from_the_commit_date(site, repo):
    """Not from the build clock.

    Deliberately not asserting that the values differ: pages changed in the
    same commit share a date, and a fresh CI checkout gives every file the
    same mtime, so distinctness is not a property of a correct sitemap.
    """
    committed = subprocess.run(
        ['git', 'log', '-1', '--format=%cI', '--', 'content/pages/index.rst'],
        cwd=repo, capture_output=True, text=True)
    if committed.returncode != 0 or not committed.stdout.strip():
        pytest.skip('no git history available')

    expected = datetime.fromisoformat(committed.stdout.strip())
    home = re.search(
        r'<loc>[^<]*rnaforecast\.com/</loc>\s*<lastmod>([^<]+)</lastmod>',
        read(site / 'sitemap.xml'))
    assert home, 'home page missing from the sitemap'
    assert datetime.fromisoformat(home.group(1)) == expected


def test_rebuilding_does_not_move_lastmod(site, tmp_path, repo):
    """The whole point: an unchanged rebuild must not look like a change."""
    again = tmp_path / 'again'
    result = subprocess.run(
        [sys.executable, '-m', 'pelican', 'content', '-o', str(again),
         '-s', 'publishconf.py'],
        cwd=repo, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr

    first = re.findall(r'<lastmod>([^<]+)</lastmod>', read(site / 'sitemap.xml'))
    second = re.findall(r'<lastmod>([^<]+)</lastmod>', read(again / 'sitemap.xml'))
    assert first == second and first


# --- llms.txt -------------------------------------------------------------

def test_llms_txt_describes_the_real_pages(site):
    llms = read(site / 'llms.txt')
    assert llms.startswith('# RNA Forecast')
    for path in ['/research/', '/publications/', '/about/']:
        assert f'https://rnaforecast.com{path}' in llms


def test_llms_txt_links_resolve(site):
    llms = read(site / 'llms.txt')
    for url in re.findall(r'https://rnaforecast\.com(/[^)\s]*)', llms):
        target = site / url.strip('/')
        if target.suffix:
            assert target.is_file(), url
        else:
            assert (target / 'index.html').is_file() or target.is_file(), url


# --- structured data on the built site ------------------------------------

def test_the_about_page_is_a_profile_page_for_the_person(site):
    """The type Google reads to work out whose profile a page is."""
    page = site / 'about' / 'index.html'
    profile, = nodes_of(page, 'ProfilePage')
    assert profile['mainEntity'] == {'@id': AUTHOR_ID}
    assert profile['url'] == 'https://rnaforecast.com/about/'


def test_only_the_about_page_claims_to_be_a_profile(site):
    """The home page is about the platform, not the person."""
    for rel in ['index.html', 'research/index.html', 'publications/index.html']:
        assert nodes_of(site / rel, 'ProfilePage') == [], rel


def test_the_person_carries_identity_and_affiliation(site):
    person, = nodes_of(site / 'about' / 'index.html', 'Person')
    assert person['@id'] == AUTHOR_ID
    assert person['identifier'] == 'https://orcid.org/0000-0003-0925-5205'
    assert person['image'].startswith('https://rnaforecast.com/')
    assert person['affiliation'] == {'@id': 'https://rnaforecast.com/#organization'}
    assert person['knowsAbout']
    for profile in ['orcid.org', 'scholar.google', 'github.com', 'scopus.com']:
        assert any(profile in s for s in person['sameAs']), profile


def test_no_page_graph_leaves_a_dangling_reference(site):
    """A page must ship every node it points at, or it cannot be read alone."""
    for page in sorted(site.rglob('*.html')):
        for graph in graphs_in(page):
            nodes = graph.get('@graph', [])
            present = {n.get('@id') for n in nodes if n.get('@id')}

            def refs(value, out):
                if isinstance(value, dict):
                    if set(value) == {'@id'}:
                        out.add(value['@id'])
                    for item in value.values():
                        refs(item, out)
                elif isinstance(value, list):
                    for item in value:
                        refs(item, out)
                return out

            assert not (refs(nodes, set()) - present), page.name


def test_the_home_page_declares_the_person_and_organization(site):
    types = {node.get('@type')
             for graph in graphs_in(site / 'index.html')
             for node in graph.get('@graph', [])}
    assert {'Person', 'Organization', 'WebPage'} <= types


def test_every_publication_reaches_the_graph(site):
    page = site / 'publications' / 'index.html'
    articles = nodes_of(page, 'ScholarlyArticle')
    assert len(articles) == read(page).count('class="pub-title"')
    assert all('@id' in a for a in articles), 'every paper should carry its DOI'


def test_every_doi_on_the_page_is_described(site):
    page = site / 'publications' / 'index.html'
    linked = set(re.findall(r'https://doi\.org/(10\.[^"\'<\s]+)', read(page)))
    described = {a['identifier']['value'] for a in nodes_of(page, 'ScholarlyArticle')}
    assert linked <= described


def test_the_author_node_is_the_same_entity_across_pages(site):
    """The hand-written home graph and the generated one must not fork."""
    home = {n['@id'] for n in nodes_of(site / 'index.html', 'Person')}
    pubs = {n['@id'] for n in nodes_of(site / 'publications' / 'index.html', 'Person')}
    assert home == pubs == {AUTHOR_ID}


def test_articles_are_attributed_to_that_node(site):
    articles = nodes_of(site / 'publications' / 'index.html', 'ScholarlyArticle')
    attributed = [a for a in articles
                  if any(author.get('@id') == AUTHOR_ID
                         for author in a.get('author', []))]
    assert len(attributed) == len(articles)
