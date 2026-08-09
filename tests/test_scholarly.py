"""Unit tests for the publication structured-data extractor.

The plugin reads rendered markup, so these fixtures are the two shapes the
site actually produces: the full listing on /publications/ and the compact
one on the home page.
"""

import json

import pytest

from plugins import scholarly

SITE = 'https://rnaforecast.com'
AUTHOR_ID = f'{SITE}/#michael-t-wolfinger'

FULL = """
<div class="pub-group" id="y2026">
  <div class="pub">
    <div class="pub-meta">
      <div class="pub-badge">Nucleic Acids Research</div>
      <div class="pub-type">Journal article</div>
    </div>
    <div class="pub-body">
      <div class="pub-title">Rational design of mechanically active RNAs</div>
      <div class="pub-authors">Walter, Hofacker, <strong>Michael T. Wolfinger</strong></div>
      <div class="pub-cite">Nucleic Acids Res. 54(9):gkag473 (2026)</div>
      <div class="pub-summary">Reports the rational engineering of xrRNAs.</div>
      <div class="pub-links">
        <a href="https://doi.org/10.1093/nar/gkag473">DOI</a>
        <div class="pub-doi">doi:10.1093/nar/gkag473</div>
      </div>
    </div>
  </div>
</div>
"""

# No .pub-group, no .pub-doi: the DOI is only in the link, the journal is a
# .tag, the year is a .pub-year, and the author is abbreviated.
COMPACT = """
<div class="pubs">
  <div class="pub">
    <div class="pub-year">2025</div>
    <div class="pub-body">
      <div class="tag tag-outline">Nature Biotechnology</div>
      <div class="pub-title">Conserved RNA regulatory switches</div>
      <div class="pub-authors">Borovsk&aacute;, <strong>Wolfinger MT</strong>, Incarnato</div>
      <div class="pub-links">
        <a href="https://doi.org/10.1038/s41587-025-02739-0">doi:10.1038/s41587-025-02739-0</a>
      </div>
    </div>
  </div>
</div>
"""


def build(html):
    return scholarly.build_graph(html, f'{SITE}/publications/', 'Publications', SITE)


def articles(html):
    graph = build(html)
    if graph is None:
        return []
    return [n for n in graph['@graph'] if n.get('@type') == 'ScholarlyArticle']


def test_full_listing_yields_a_complete_article():
    article, = articles(FULL)
    assert article['name'] == 'Rational design of mechanically active RNAs'
    assert article['@id'] == 'https://doi.org/10.1093/nar/gkag473'
    assert article['identifier']['value'] == '10.1093/nar/gkag473'
    assert article['datePublished'] == '2026'
    assert article['isPartOf']['name'] == 'Nucleic Acids Research'
    assert article['abstract'].startswith('Reports the rational')


def test_compact_layout_recovers_doi_journal_and_year():
    article, = articles(COMPACT)
    assert article['@id'] == 'https://doi.org/10.1038/s41587-025-02739-0'
    assert article['isPartOf']['name'] == 'Nature Biotechnology'
    assert article['datePublished'] == '2025'


@pytest.mark.parametrize('html', [FULL, COMPACT])
def test_the_site_author_is_a_reference_to_one_shared_node(html):
    article, = articles(html)
    refs = [a for a in article['author'] if set(a) == {'@id'}]
    assert refs == [{'@id': AUTHOR_ID}], 'both spellings must reach one node'


@pytest.mark.parametrize('html', [FULL, COMPACT])
def test_coauthors_are_plain_people(html):
    article, = articles(html)
    named = [a for a in article['author'] if 'name' in a]
    assert named and all(a['@type'] == 'Person' for a in named)


def test_author_node_is_declared_with_its_orcid():
    graph = build(FULL)
    person = graph['@graph'][0]
    assert person['@id'] == AUTHOR_ID
    assert person['identifier'] == scholarly.AUTHOR_ORCID


def test_only_a_real_listing_claims_to_be_a_collection():
    types = [n.get('@type') for n in build(FULL)['@graph']]
    assert 'CollectionPage' in types

    types = [n.get('@type') for n in build(COMPACT)['@graph']]
    assert 'CollectionPage' not in types, (
        'a page that merely features papers is not the bibliography')


def test_collection_lists_every_article():
    graph = build(FULL)
    collection, = [n for n in graph['@graph']
                   if n.get('@type') == 'CollectionPage']
    assert collection['hasPart'] == [{'@id': 'https://doi.org/10.1093/nar/gkag473'}]


def test_a_publication_without_a_doi_still_appears():
    html = FULL.replace('<div class="pub-doi">doi:10.1093/nar/gkag473</div>', '')
    html = html.replace('<a href="https://doi.org/10.1093/nar/gkag473">DOI</a>', '')
    article, = articles(html)
    assert '@id' not in article
    assert article['name']


def test_a_block_without_a_title_is_skipped():
    html = FULL.replace('class="pub-title"', 'class="pub-nothing"')
    assert articles(html) == []
    assert build(html) is None, 'nothing extractable means no graph at all'


def test_the_emphasised_name_keeps_its_place_in_the_author_list():
    """Document order must survive parsing, wherever the name sits."""
    html = FULL.replace(
        '<div class="pub-authors">Walter, Hofacker, '
        '<strong>Michael T. Wolfinger</strong></div>',
        '<div class="pub-authors">Walter, '
        '<strong>Michael T. Wolfinger</strong>, Hofacker</div>')
    article, = articles(html)
    names = [a.get('name', a.get('@id')) for a in article['author']]
    assert names == ['Walter', AUTHOR_ID, 'Hofacker']


def test_pages_with_no_publications_produce_no_graph():
    assert build('<p>Nothing here.</p>') is None


def test_script_body_cannot_close_its_own_element():
    """A '<' reaching the graph must not be able to end the script element."""
    graph = {'@context': 'https://schema.org',
             '@graph': [{'@type': 'ScholarlyArticle',
                         'name': 'Escaping </script><script>alert(1)</script>',
                         'abstract': 'a & b > c'}]}
    body = scholarly.to_script_body(graph)

    assert '<' not in body and '>' not in body and '&' not in body
    # The escapes are JSON, so the data survives intact.
    assert json.loads(body)['@graph'][0]['name'].endswith('</script>')
    assert json.loads(body)['@graph'][0]['abstract'] == 'a & b > c'


def test_entities_in_markup_are_decoded():
    article, = articles(COMPACT)
    names = [a.get('name', '') for a in article['author']]
    assert any('á' in name for name in names), names
