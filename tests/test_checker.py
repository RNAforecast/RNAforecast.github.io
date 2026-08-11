"""The smoke checker must actually catch things.

A checker that only ever passes is worse than no checker, so each fault class
is injected into a real build and the checker is required to report it.
"""

import pytest

from scripts import check_build

from conftest import read


def problems_for(root):
    problems, _ = check_build.check(str(root))
    return problems


def assert_reports(root, fragment):
    found = problems_for(root)
    assert any(fragment in p for p in found), (
        f'expected a problem mentioning {fragment!r}, got: {found}')


def test_a_missing_page_is_caught(sabotaged):
    (sabotaged / 'publications' / 'index.html').unlink()
    assert_reports(sabotaged, 'missing: publications/index.html')


def test_a_broken_asset_reference_is_caught(sabotaged):
    page = sabotaged / 'research' / 'index.html'
    page.write_text(read(page).replace('css/rnaf.css', 'css/gone.css'))
    assert_reports(sabotaged, 'broken reference')


def test_a_broken_absolute_internal_link_is_caught(sabotaged):
    page = sabotaged / 'index.html'
    page.write_text(read(page).replace(
        'https://rnaforecast.com/about/', 'https://rnaforecast.com/vanished/'))
    assert_reports(sabotaged, 'vanished')


def test_a_third_party_subresource_is_caught(sabotaged):
    page = sabotaged / 'about' / 'index.html'
    page.write_text(read(page).replace(
        '<head>',
        '<head><link rel="stylesheet" href="https://fonts.googleapis.com/css2">',
        1))
    assert_reports(sabotaged, 'third-party request to fonts.googleapis.com')


def test_an_outbound_link_is_not_mistaken_for_a_request(sabotaged):
    """DOI and ORCID links are followed by readers, not fetched by browsers."""
    page = sabotaged / 'legal' / 'index.html'
    page.write_text(read(page).replace(
        '<body>', '<body><a href="https://doi.org/10.1234/xyz">DOI</a>', 1))
    assert problems_for(sabotaged) == []


def test_stray_inline_script_is_caught(sabotaged):
    page = sabotaged / 'legal' / 'index.html'
    page.write_text(read(page).replace(
        '</body>', '<script>alert("hi")</script></body>', 1))
    assert_reports(sabotaged, 'unexpected inline <script>')


def test_the_analytics_and_consent_blocks_are_allowed(site):
    """Production legitimately emits these; they must not be flagged."""
    html = read(site / 'index.html')
    assert 'window.dataLayer' in html
    assert "gtag('js'" in html
    assert problems_for(site) == []


def test_broken_jsonld_is_caught(sabotaged):
    page = sabotaged / 'publications' / 'index.html'
    page.write_text(read(page).replace('"@context"', '"@context",', 1))
    assert_reports(sabotaged, 'JSON-LD does not parse')


def test_a_publication_missing_from_the_graph_is_caught(sabotaged):
    """The count check is what protects against silent extractor breakage."""
    page = sabotaged / 'publications' / 'index.html'
    html = read(page)
    start = html.index('<script type="application/ld+json">')
    end = html.index('</script>', start) + len('</script>')
    page.write_text(html[:start] + html[end:])
    assert_reports(sabotaged, 'in the JSON-LD graph')


def test_a_broken_font_reference_in_css_is_caught(sabotaged):
    """Nothing links the fonts from HTML, so only the CSS scan can see this."""
    sheet = sabotaged / 'css' / 'rnaf.css'
    sheet.write_text(read(sheet).replace('barlow-400-latin.woff2',
                                         'barlow-gone.woff2'))
    assert_reports(sabotaged, 'does not resolve')


def test_a_font_cdn_in_css_is_caught(sabotaged):
    sheet = sabotaged / 'css' / 'rnaf.css'
    sheet.write_text('@font-face { src: url(https://fonts.gstatic.com/x.woff2); }\n'
                     + read(sheet))
    assert_reports(sabotaged, 'third-party request to fonts.gstatic.com')


def test_every_shipped_font_is_actually_referenced(site):
    sheet = read(site / 'css' / 'rnaf.css')
    fonts = {p.name for p in (site / 'static' / 'fonts').glob('*.woff2')}
    assert fonts, 'the site self-hosts its fonts'
    assert all(name in sheet for name in fonts), fonts


def test_a_form_posting_somewhere_new_is_caught(sabotaged):
    """A form action is a data flow and needs a disclosure, so it must not
    change silently."""
    page = sabotaged / 'index.html'
    page.write_text(read(page).replace('https://formsubmit.co/',
                                       'https://evil.example.com/'))
    assert_reports(sabotaged, 'form posts to evil.example.com')


def test_the_declared_form_endpoint_is_accepted(site):
    assert 'formsubmit.co' in read(site / 'index.html')
    assert problems_for(site) == []


def test_analytics_loading_before_the_consent_defaults_is_caught(sabotaged):
    """The failure that makes a consent banner decorative."""
    page = sabotaged / 'index.html'
    html = read(page)
    start = html.index("<script>\n  window.dataLayer")
    end = html.index('</script>', start) + len('</script>')
    block = html[start:end]
    html = html[:start] + html[end:]
    # move the defaults to after the Google tag
    tag_end = html.index('</script>', html.index('googletagmanager.com/gtag/js'))
    page.write_text(html[:tag_end] + block + html[tag_end:])
    assert_reports(sabotaged, 'come after the Google tag')


def test_the_cmp_loading_after_analytics_is_caught(sabotaged):
    page = sabotaged / 'index.html'
    html = read(page)
    osano = '  <script src="https://cmp.osano.com/'
    start = html.index(osano)
    end = html.index('</script>', start) + len('</script>') + 1
    block = html[start:end]
    html = html[:start] + html[end:]
    tag_end = html.index('</script>', html.index('googletagmanager.com/gtag/js')) + 9
    page.write_text(html[:tag_end] + '\n' + block + html[tag_end:])
    assert_reports(sabotaged, 'loads after the Google tag')


def test_analytics_granted_by_default_is_caught(sabotaged):
    page = sabotaged / 'index.html'
    page.write_text(read(page).replace("analytics_storage: 'denied'",
                                       "analytics_storage: 'granted'"))
    assert_reports(sabotaged, 'not denied by default')


def test_the_shipped_consent_order_is_correct(site):
    html = read(site / 'index.html')
    default = html.index("gtag('consent', 'default'")
    cmp_at = html.index('osano.js')
    tag = html.index('googletagmanager.com/gtag/js')
    assert default < cmp_at < tag, 'defaults, then the CMP, then the tag'
    assert problems_for(site) == []


def test_a_field_parsed_as_a_list_is_caught(sabotaged):
    """"J. General Virology" became <ol start="10">, losing the "J." and
    printing "10." on the page."""
    page = sabotaged / 'publications' / 'index.html'
    page.write_text(read(page).replace(
        '<div class="pub-badge">\nJournal of General Virology</div>',
        '<div class="pub-badge">\n<ol start="10">\n<li>General Virology</li>\n</ol>\n</div>',
        1))
    assert_reports(sabotaged, 'was parsed as a list')


def test_no_publication_field_is_a_list(site):
    html = read(site / 'publications' / 'index.html')
    assert '<ol start=' not in html
    assert 'Journal of General Virology' in html


def test_a_wrong_sized_share_card_is_caught(sabotaged):
    card = sabotaged / check_build.OG_CARD
    card.write_bytes(b'not a png at all')
    assert_reports(sabotaged, 'not a PNG')


def test_a_missing_sitemap_line_in_robots_is_caught(sabotaged):
    robots = sabotaged / 'robots.txt'
    robots.write_text(
        '\n'.join(line for line in read(robots).splitlines()
                  if not line.lower().startswith('sitemap:')))
    assert_reports(sabotaged, 'no Sitemap: line')


def test_an_excluded_page_appearing_in_the_sitemap_is_caught(sabotaged):
    sitemap = sabotaged / 'sitemap.xml'
    sitemap.write_text(read(sitemap).replace(
        '</urlset>',
        '<url><loc>https://rnaforecast.com/legal/</loc></url></urlset>'))
    assert_reports(sabotaged, 'which is excluded')


def test_a_sitemap_url_that_does_not_exist_is_caught(sabotaged):
    sitemap = sabotaged / 'sitemap.xml'
    sitemap.write_text(read(sitemap).replace(
        '</urlset>',
        '<url><loc>https://rnaforecast.com/imaginary/</loc></url></urlset>'))
    assert_reports(sabotaged, 'does not exist')


def test_a_page_without_a_canonical_is_caught(sabotaged):
    page = sabotaged / 'about' / 'index.html'
    page.write_text(read(page).replace('<link rel="canonical"', '<link rel="x"'))
    assert_reports(sabotaged, 'no canonical link')


@pytest.mark.parametrize('data, expected', [
    (b'\x89PNG\r\n\x1a\n' + b'\x00' * 8 + (1200).to_bytes(4, 'big')
     + (630).to_bytes(4, 'big'), (1200, 630)),
    (b'not a png', None),
])
def test_png_size_reads_the_header(tmp_path, data, expected):
    path = tmp_path / 'x.png'
    path.write_bytes(data)
    assert check_build.png_size(path) == expected
