"""The LaTeX → PDF + RST pipeline.

LaTeX is the scientific source of truth for an Insight. These tests guard the
one rule that makes that true in practice: the committed
content/insights/<slug>.rst must be exactly what the canonical sources
produce, so a scientific correction cannot be made by editing the generated
file and forgetting the manuscript.

The conversion tests need pandoc and skip without it; the tests that read the
committed files run everywhere, including on a machine with no LaTeX.
"""

import re
import shutil

import pytest
import yaml

from conftest import nodes_of, read

from scripts import build_insight, check_insight

SLUG = 'rna-structure-before-the-experiment'

needs_pandoc = pytest.mark.skipif(
    shutil.which('pandoc') is None,
    reason='pandoc is not installed; the Insight web build needs it')


@pytest.fixture(scope='module')
def slugs():
    found = check_insight.insight_slugs()
    if not found:
        pytest.skip('no Insight sources')
    return found


@pytest.fixture(scope='module')
def meta(repo):
    with open(repo / 'insights' / SLUG / 'metadata.yaml', encoding='utf-8') as f:
        return yaml.safe_load(f)


# --- the canonical sources exist and are the only source ------------------

def test_every_insight_has_its_canonical_sources(repo, slugs):
    for slug in slugs:
        src = repo / 'insights' / slug
        for name in ('manuscript.tex', 'references.bib', 'metadata.yaml'):
            assert (src / name).is_file(), f'{slug}/{name}'


def test_the_manuscript_carries_no_website_furniture(repo, slugs):
    """Navigation, CTAs and contact details belong to the templates."""
    for slug in slugs:
        tex = read(repo / 'insights' / slug / 'manuscript.tex')
        body = '\n'.join(line for line in tex.splitlines()
                         if not line.lstrip().startswith('%'))
        for forbidden in ['All Insights', 'insight-cta', 'rnaforecast.com',
                          '/research/', '/publications/', 'mailto:']:
            assert forbidden not in body, f'{slug}: {forbidden} in manuscript'


def test_the_manuscript_never_writes_a_reference_number(repo, slugs):
    """Numbering comes from citation order, in both outputs."""
    for slug in slugs:
        tex = read(repo / 'insights' / slug / 'manuscript.tex')
        assert not re.search(r'\[\d+\]', tex), slug


def test_the_generated_article_says_it_is_generated(repo, slugs):
    for slug in slugs:
        rst = read(repo / 'content' / 'insights' / f'{slug}.rst')
        head = rst.split('\n\n')[0]
        assert 'DO NOT EDIT' in head, slug
        assert f'insights/{slug}/manuscript.tex' in head, slug


def test_no_insight_is_maintained_twice(repo, slugs):
    """One .rst per Insight, and it is the generated one."""
    generated = {f'{slug}.rst' for slug in slugs}
    present = {p.name for p in (repo / 'content' / 'insights').glob('*.rst')}
    assert present == generated, present ^ generated


# --- metadata is stated once ----------------------------------------------

def test_pelican_metadata_comes_from_the_yaml(repo, meta):
    rst = read(repo / 'content' / 'insights' / f'{SLUG}.rst')
    for field in ('title', 'subtitle', 'slug', 'author', 'status',
                  'description', 'summary', 'version'):
        value = ' '.join(str(meta[field]).split())
        assert value in ' '.join(rst.split()), field
    assert f":date: {meta['date']}" in rst
    for tag in meta['tags']:
        assert tag in rst


def test_the_published_page_states_the_canonical_metadata(site, meta):
    if meta['status'] != 'published':
        pytest.skip('the Insight is a draft')
    html = read(site / 'insights' / SLUG / 'index.html')
    assert meta['title'] in html
    assert meta['subtitle'] in html
    assert f"Version {meta['version']}" in html
    assert f"{meta['series']} {meta['number']}" in html


def test_the_abstract_is_bibliographic_data_not_page_text(site, meta):
    """It belongs to the deposit record and the graph, not to the article.

    The article already opens with its lead; printing the abstract above it
    says the same thing twice. docutils reserves the name `abstract` for a
    body topic, which is exactly the accident this guards against.
    """
    if meta['status'] != 'published' or not meta.get('abstract'):
        pytest.skip('no published abstract')
    html = read(site / 'insights' / SLUG / 'index.html')
    article, = nodes_of(site / 'insights' / SLUG / 'index.html', 'Article')
    assert article['abstract'] == ' '.join(meta['abstract'].split())
    assert article['abstract'] != article['description']

    body = html.split('<article>', 1)[1]
    opening = ' '.join(meta['abstract'].split())[:60]
    assert opening not in body, 'the abstract was printed into the page'
    assert '<aside class="abstract">' not in html


def test_an_insight_cannot_be_published_without_an_abstract(repo, tmp_path,
                                                            monkeypatch):
    """Every published Insight is deposited, and a deposit needs one."""
    src = repo / 'insights' / SLUG / 'metadata.yaml'
    data = yaml.safe_load(read(src))
    data['status'] = 'published'
    data.pop('abstract', None)

    work = tmp_path / 'insights' / SLUG
    work.mkdir(parents=True)
    (work / 'metadata.yaml').write_text(yaml.safe_dump(data), encoding='utf-8')
    monkeypatch.setattr(build_insight, 'INSIGHTS', str(tmp_path / 'insights'))

    with pytest.raises(build_insight.BuildError, match='abstract'):
        build_insight.load_metadata(SLUG)


def test_the_deposit_metadata_matches_the_canonical_record(tmp_path, meta):
    """What gets pasted into Zenodo is generated, not retyped."""
    if meta['status'] != 'published':
        pytest.skip('the Insight is a draft')
    from datetime import date as date_type
    prepared = {**meta}
    for field in ('date', 'modified'):
        if not isinstance(prepared[field], date_type):
            pytest.skip('unexpected date type')

    path = build_insight.write_deposit_metadata(SLUG, prepared, str(tmp_path))
    text = read(path)
    assert meta['title'] in text and meta['subtitle'] in text
    assert meta['affiliation_formal'] in text
    assert meta['affiliation'] not in text, 'the deposit takes the formal one'
    assert f'https://rnaforecast.com/insights/{SLUG}/' in text
    assert ' '.join(meta['abstract'].split()) in ' '.join(text.split())
    assert str(meta['version']) in text
    assert meta['copyright'] in text
    assert meta['resource_type'] in text


def test_the_copyright_names_a_person(meta):
    """Only a natural person can be an author under Austrian law, so the
    e.U. is the publisher, never the rights holder."""
    statement = meta.get('copyright')
    if not statement:
        pytest.skip('no copyright statement')
    assert meta['author'] in statement
    assert 'e.U.' not in statement
    assert meta['license'] in statement, 'the statement should name the licence'


def test_a_doi_would_reach_both_the_page_and_its_structured_data(site, meta):
    """Until one is reserved there is no citation block, and that is correct."""
    if meta['status'] != 'published':
        pytest.skip('the Insight is a draft')
    html = read(site / 'insights' / SLUG / 'index.html')
    if meta.get('doi'):
        assert f"doi:{meta['doi']}" in html
        assert f"https://doi.org/{meta['doi']}" in html
    else:
        assert 'Cite this Insight' not in html


def test_the_citation_block_says_which_version_it_is(site, meta):
    """The deposit is versioned, so a citation of it has to be too —
    otherwise the page and the Zenodo record identify the work differently."""
    if meta['status'] != 'published' or not meta.get('doi'):
        pytest.skip('no published DOI, so no citation block')
    html = read(site / 'insights' / SLUG / 'index.html')
    # From the heading to the start of the next block, which is the CTA.
    block = html.split('Cite this Insight', 1)[1].split('insight-cta', 1)[0]
    assert block.strip(), 'the citation block came out empty'
    for needed in (meta['author'], str(meta['series']), str(meta['number']),
                   f"Version {meta['version']}", str(meta['doi'])):
        assert needed in block, needed


# --- the conversion itself ------------------------------------------------

@needs_pandoc
def test_regenerating_reproduces_the_committed_article(repo, slugs):
    """The check CI runs: nobody edited the generated RST by hand."""
    problems, warnings = [], []
    for slug in slugs:
        meta = build_insight.load_metadata(slug)
        check_insight.check_generated_rst(slug, meta, problems, warnings)
    assert problems == [], '\n'.join(problems)
    for warning in warnings:
        print(f'note: {warning}')


@needs_pandoc
def test_citation_order_follows_the_manuscript(repo):
    """Reordering the prose must renumber the references, not the author."""
    src = repo / 'insights' / SLUG / 'manuscript.tex'
    _, cited, _ = build_insight.convert_body(SLUG, str(src))
    # Comments carry an example \cite; pandoc ignores them and so must this.
    tex = '\n'.join(line for line in read(src).splitlines()
                    if not line.lstrip().startswith('%'))
    first_seen = []
    for match in re.finditer(r'\\cite\{([^}]*)\}', tex):
        for key in (k.strip() for k in match.group(1).split(',')):
            if key and key not in first_seen:
                first_seen.append(key)
    assert cited == first_seen

    rst = read(repo / 'content' / 'insights' / f'{SLUG}.rst')
    defined = re.findall(r'^\s*\.\. \[#([^\]]+)\]', rst, re.M)
    assert defined == cited, 'the reference list is not in citation order'


@needs_pandoc
def test_no_raw_latex_escapes_into_the_website(repo, slugs):
    for slug in slugs:
        rst = read(repo / 'content' / 'insights' / f'{slug}.rst')
        assert ':raw-latex:' not in rst, slug
        assert '\\cite{' not in rst, slug


@needs_pandoc
def test_an_undefined_citation_key_fails_the_build(repo, tmp_path, monkeypatch):
    """The build must not quietly ship an article with a dangling citation."""
    work = tmp_path / 'insights'
    shutil.copytree(repo / 'insights', work)
    tex_path = work / SLUG / 'manuscript.tex'
    tex_path.write_text(
        tex_path.read_text(encoding='utf-8')
        .replace('\\cite{kudla2009}', '\\cite{nosuchkey2099}'),
        encoding='utf-8')
    monkeypatch.setattr(build_insight, 'INSIGHTS', str(work))
    monkeypatch.setattr(build_insight, 'TEMPLATES', str(work / 'templates'))

    meta = build_insight.load_metadata(SLUG)
    with pytest.raises(build_insight.BuildError, match='undefined citation'):
        build_insight.build_web(SLUG, meta, out_dir=str(tmp_path / 'out'),
                                quiet=True)


# --- conversion edge cases ------------------------------------------------
#
# tests/fixtures/insight-conversion/ is a manuscript that uses every construct
# the converter has had to be taught: multiple citations at one place, a
# scientific footnote, an equation, a table and a figure with cross-references,
# unicode, superscripts and quotations. Each assertion below is a pandoc
# behaviour that produced broken output until it was handled.

@pytest.fixture(scope='module')
def converted(repo):
    tex = repo / 'tests' / 'fixtures' / 'insight-conversion' / 'manuscript.tex'
    body, cited, notes = build_insight.convert_body('fixture', str(tex))
    return body, cited, notes


@needs_pandoc
def test_several_citations_at_one_place_become_several_markers(converted):
    body, cited, _ = converted
    assert '[#mueller2020]_ [#pre2026]_' in body
    assert cited[:2] == ['mueller2020', 'pre2026']


@needs_pandoc
def test_a_footnote_joins_the_reference_sequence(converted):
    """It must not take [1] and push the first reference to [2]."""
    body, cited, notes = converted
    assert notes == {'fn1': 'The footnote text.'}
    assert '.. [#fn1]' not in body, 'the note should be lifted out of the body'
    assert cited.index('fn1') > cited.index('mueller2020')


@needs_pandoc
def test_a_figure_keeps_the_anchor_its_label_asked_for(converted):
    """Pandoc writes the `name` option without its colon."""
    body, _, _ = converted
    assert '   :name: fig:one' in body
    assert '\n   name: fig:one' not in body


@pytest.mark.parametrize('emitted', [
    '   name: fig:one\n',          # pandoc 3.11: the option, minus its colon
    '   :name: fig:one\n',         # a version that writes it correctly
    '   :alt: \n',                 # the pandoc on CI: no name at all
    '',                            # nothing but the directive
])
def test_a_figure_is_named_whatever_pandoc_did(emitted):
    """The anchor comes from the manuscript, not from pandoc's RST writer.

    That writer has emitted a figure's name three different ways across
    versions, so relying on any of them makes the build depend on which
    pandoc happens to be installed — which is how CI and a laptop start
    producing different articles from one source.
    """
    tex = r'\begin{figure}\includegraphics{f.png}\caption{C}\label{fig:one}\end{figure}'
    body = f'.. figure:: f.png\n{emitted}\n   C\n\nFigure `1 <#fig-one>`__.\n'
    named = build_insight.name_figures(body, tex)
    assert '   :name: fig:one' in named
    assert named.count(':name:') == 1
    assert '\n   name: fig:one' not in named


@needs_pandoc
def test_a_table_keeps_the_anchor_its_label_asked_for(converted):
    """Pandoc drops a table's label entirely; it is recovered from the .tex."""
    body, _, _ = converted
    assert re.search(r'\.\. table::.*\n\s+:name: tab:one', body)


@needs_pandoc
def test_cross_references_point_at_the_id_docutils_will_create(converted):
    body, _, _ = converted
    assert '<#fig-one>`__' in body and '<#tab-one>`__' in body
    assert '<#fig:one>' not in body


@needs_pandoc
def test_an_equation_is_something_docutils_can_render(converted):
    """A nested `equation` environment makes docutils drop the whole page."""
    body, _, _ = converted
    assert '.. math::' in body
    assert '\\begin{equation}' not in body
    assert '\\label{' not in body
    assert ':name: eq:gibbs' in body


@needs_pandoc
def test_a_directive_is_never_split_from_its_options(converted):
    body, _, _ = converted
    for match in re.finditer(r'^([ \t]*)\.\. \w+::.*$', body, re.M):
        rest = body[match.end():].split('\n')
        if len(rest) > 2 and rest[1].strip().startswith(':'):
            assert rest[0].strip() == '' or rest[1].strip().startswith(':'), \
                'a blank line was inserted before an option block'


@needs_pandoc
def test_unicode_and_superscripts_survive(converted):
    body, _, _ = converted
    assert 'N\\ :sup:`6`' in body
    assert '5′' in body and '3′' in body
    assert '1990–2020' in body and '—' in body
    assert '“quotations”' in body


@needs_pandoc
def test_a_figure_is_copied_into_the_site_and_repointed(repo, tmp_path):
    fixture = repo / 'tests' / 'fixtures' / 'insight-conversion'
    work = tmp_path / 'insights'
    (work / 'probe').mkdir(parents=True)
    for name in ('manuscript.tex', 'references.bib'):
        shutil.copy(fixture / name, work / 'probe' / name)
    shutil.copytree(fixture / 'figures', work / 'probe' / 'figures')

    out = tmp_path / 'content' / 'insights'
    out.mkdir(parents=True)
    monkey = build_insight.INSIGHTS
    build_insight.INSIGHTS = str(work)
    try:
        body, _, _ = build_insight.convert_body(
            'probe', str(work / 'probe' / 'manuscript.tex'))
        body = build_insight.publish_figures('probe', body, str(out), True)
    finally:
        build_insight.INSIGHTS = monkey

    assert '.. figure:: /static/insights/probe/diagram.png' in body
    copied = tmp_path / 'content' / 'static' / 'insights' / 'probe' / 'diagram.png'
    assert copied.is_file()


@needs_pandoc
def test_the_house_bibliography_style(repo):
    """Author truncation, italics, DOIs and preprint marking."""
    bib = repo / 'tests' / 'fixtures' / 'insight-conversion' / 'references.bib'
    entries, preprints = build_insight.load_bibliography(str(bib))
    assert preprints == {'pre2026'}

    rendered = build_insight.render_references(
        ['mueller2020', 'pre2026'], entries, preprints)
    assert 'Müller J-A, Østergaard L, Fernández JA.' in rendered
    assert 'Doe J, Roe R, Poe E, et al.' in rendered, 'six authors are cut'
    assert '*RNA* 26:1–12 (2020).' in rendered
    assert 'Preprint.' in rendered
    assert '`doi:10.1261/rna.000000 <https://doi.org/10.1261/rna.000000>`__' \
        in rendered


def test_a_preprint_is_never_presented_as_peer_reviewed(repo):
    bib = read(repo / 'insights' / SLUG / 'references.bib')
    preprints = build_insight.preprint_keys(
        str(repo / 'insights' / SLUG / 'references.bib'))
    if not preprints:
        pytest.skip('nothing cited is a preprint')
    rst = read(repo / 'content' / 'insights' / f'{SLUG}.rst')
    for key in preprints:
        entry = re.search(rf'\.\. \[#{re.escape(key)}\](.*?)(?=\n  \.\. \[#|\Z)',
                          rst, re.S)
        assert entry, key
        assert 'Preprint.' in entry.group(1), f'{key} is not marked a preprint'


def test_metadata_that_is_incomplete_cannot_be_published(repo, tmp_path,
                                                         monkeypatch):
    """`status: published` with a hole in the metadata must fail the build."""
    import os
    src = repo / 'insights' / SLUG / 'metadata.yaml'
    meta = yaml.safe_load(read(src))
    meta['status'] = 'published'
    meta['description'] = ''

    work = tmp_path / 'insights' / SLUG
    work.mkdir(parents=True)
    (work / 'metadata.yaml').write_text(yaml.safe_dump(meta), encoding='utf-8')
    monkeypatch.setattr(build_insight, 'INSIGHTS', str(tmp_path / 'insights'))

    with pytest.raises(build_insight.BuildError, match='missing description'):
        build_insight.load_metadata(SLUG)
