"""The Insights section.

Insights are Pelican articles under the hood and a curated library in public,
so the tests here hold that line: the URLs, the metadata and the structured
data that make an Insight a first-class page, and the wording that must never
call the section a blog.

Most of these run against whatever is published. With every Insight still in
draft the article-level tests skip rather than fail, which is the state the
section ships in before the first piece is approved.
"""

import json
import re

import pytest

from conftest import graphs_in, nodes_of, read

LIBRARY = 'insights/index.html'


def insights(site):
    return sorted(site.glob('insights/*/index.html'))


@pytest.fixture
def published(site):
    found = insights(site)
    if not found:
        pytest.skip('no Insight is published yet')
    return found


# --- the library ----------------------------------------------------------

def test_the_library_page_is_built(site):
    assert (site / LIBRARY).is_file()


def test_the_library_is_indexable(site):
    html = read(site / LIBRARY)
    assert 'noindex' not in html
    assert '<link rel="canonical" href="https://rnaforecast.com/insights/"' in html


def test_the_library_is_in_the_sitemap(site):
    assert '<loc>https://rnaforecast.com/insights/</loc>' in read(site / 'sitemap.xml')


def test_the_masthead_offers_insights_everywhere(site):
    for page in sorted(site.rglob('*.html')):
        assert 'https://rnaforecast.com/insights/' in read(page), page


def test_the_current_section_is_marked_on_the_library_page(site):
    assert re.search(r'<a href="https://rnaforecast\.com/insights/"'
                     r' aria-current="page"', read(site / LIBRARY))


def test_the_ui_never_calls_the_section_a_blog(site):
    """Pelican may think in articles; the reader never sees the word."""
    for page in sorted(site.rglob('*.html')):
        assert 'blog' not in read(page).lower(), page


def test_no_blog_furniture_is_generated(site):
    """Category, tag, author and archive listings stay off."""
    for stray in ['tags.html', 'categories.html', 'authors.html',
                  'archives.html', 'category', 'tag', 'author', 'drafts']:
        assert not (site / stray).exists(), stray


def test_the_library_declares_a_collection_page(site):
    collection, = nodes_of(site / LIBRARY, 'CollectionPage')
    assert collection['url'] == 'https://rnaforecast.com/insights/'


def test_the_library_lists_every_published_insight(site, published):
    html = read(site / LIBRARY)
    collection, = nodes_of(site / LIBRARY, 'CollectionPage')
    items = collection['mainEntity']['itemListElement']
    assert len(items) == len(published)

    for page in published:
        url = f'https://rnaforecast.com/insights/{page.parent.name}/'
        assert f'href="{url}"' in html, url
        assert any(item['url'] == url for item in items), url


# --- an individual Insight ------------------------------------------------

def test_insights_use_directory_style_urls(published):
    for page in published:
        assert page.name == 'index.html'
        assert page.parent.name == page.parent.name.lower()


def test_an_insight_is_a_whole_page(published):
    for page in published:
        html = read(page)
        assert html.startswith('<!DOCTYPE html>')
        assert html.count('<h1>') == 1
        assert '<link rel="canonical"' in html
        assert '<meta name="description"' in html


def test_an_insight_declares_itself_an_article(published):
    for page in published:
        html = read(page)
        assert '<meta property="og:type" content="article" />' in html
        assert '<meta property="article:published_time"' in html
        assert f'<title>' in html and '| RNA Forecast</title>' in html


def test_an_insights_canonical_matches_its_location(site, published):
    for page in published:
        url = f'https://rnaforecast.com/insights/{page.parent.name}/'
        assert f'<link rel="canonical" href="{url}" />' in read(page)


def test_an_insight_carries_article_structured_data(published):
    for page in published:
        article, = nodes_of(page, 'Article')
        assert article['headline']
        assert article['description']
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', article['datePublished'])
        assert article['author'] == {
            '@id': 'https://rnaforecast.com/#michael-t-wolfinger'}
        assert article['publisher'] == {
            '@id': 'https://rnaforecast.com/#organization'}
        assert article['image'].startswith('https://rnaforecast.com/')


def test_an_insight_ships_the_nodes_it_references(published):
    """The author and the publisher travel with the article."""
    for page in published:
        for graph in graphs_in(page):
            present = {n.get('@id') for n in graph['@graph']}
            assert {'https://rnaforecast.com/#michael-t-wolfinger',
                    'https://rnaforecast.com/#organization'} <= present


def test_an_insight_leads_back_to_the_library(published):
    for page in published:
        assert 'https://rnaforecast.com/insights/">← All Insights' in read(page)


def test_an_insight_links_into_the_rest_of_the_site(published):
    """Not an island: each piece points at the work behind it."""
    for page in published:
        html = read(page)
        assert any(f'https://rnaforecast.com{path}' in html
                   for path in ['/research/', '/publications/'])


def test_insights_are_in_the_sitemap(site, published):
    sitemap = read(site / 'sitemap.xml')
    for page in published:
        assert f'<loc>https://rnaforecast.com/insights/{page.parent.name}/</loc>' in sitemap


def test_references_and_citations_agree(published):
    """Every marker in the prose resolves, and every reference is cited.

    docutils numbers `[#key]_` footnotes and links them both ways, so this
    also catches a reference that was added and never cited.
    """
    for page in published:
        html = read(page)
        cited = set(re.findall(r'<a class="m-footnote" href="#([^"]+)"', html))
        listed = set(re.findall(r'<dt id="([^"]+)">\d+\.</dt>', html))
        if not listed:
            continue
        assert cited == listed, f'{page}: {cited ^ listed}'


def test_the_reference_list_is_a_real_definition_list(published):
    """Regression: the writer used to drop the <dl> when a footnote list was
    the first child of its container, leaving <dt>/<dd> loose and a stray
    </dl> behind — invalid markup the stylesheet could not lay out."""
    for page in published:
        html = read(page)
        if '<dt id=' not in html:
            continue
        assert html.count('<dl class="m-footnote">') == html.count('</dl>')
        assert '<dl class="m-footnote">\n<dt' in html
        assert '</a>.</dt>' not in html, 'stray </a> after a footnote label'


def test_an_insight_ships_no_javascript_of_its_own(published):
    from scripts import check_build
    for page in published:
        problems = []
        check_build.check_page(str(page.parents[2]), str(page), problems)
        assert [p for p in problems if 'inline <script>' in p] == []
