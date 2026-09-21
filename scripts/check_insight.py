#!/usr/bin/env python3
"""Validate an Insight's canonical sources and its generated outputs.

Run before publishing, and in CI. Reports one line per problem and exits
non-zero if any are fatal.

    python3 scripts/check_insight.py [slug ...] [--html DIR]

With no slug it checks every Insight. `--html` additionally checks a built
site (output-publish/), where the rendered metadata can be compared with the
canonical YAML.

What this is really guarding is the one-way rule: the committed
content/insights/<slug>.rst must be exactly what the sources produce, so that
nobody can correct the science by editing the generated file.
"""

import argparse
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_insight as bi

REPO = bi.REPO


def insight_slugs():
    if not os.path.isdir(bi.INSIGHTS):
        return []
    return sorted(
        name for name in os.listdir(bi.INSIGHTS)
        if name != 'templates'
        and os.path.isfile(os.path.join(bi.INSIGHTS, name, 'metadata.yaml')))


def check_figures(slug, problems):
    src = bi.source_dir(slug)
    with open(os.path.join(src, 'manuscript.tex'), encoding='utf-8') as f:
        tex = f.read()
    for ref in re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', tex):
        candidates = [os.path.join(src, ref),
                      os.path.join(src, 'figures', os.path.basename(ref))]
        if any(os.path.isfile(c) for c in candidates):
            continue
        if any(os.path.isfile(c + ext)
               for c in candidates for ext in ('.pdf', '.png', '.jpg', '.svg')):
            continue
        problems.append(f'{slug}: figure not found: {ref}')


def check_bibliography(slug, problems, warnings):
    src = bi.source_dir(slug)
    bib = os.path.join(src, 'references.bib')
    if not os.path.isfile(bib):
        problems.append(f'{slug}: missing references.bib')
        return
    try:
        entries, _ = bi.load_bibliography(bib)
    except bi.BuildError as exc:
        problems.append(f'{slug}: {exc}')
        return

    for key, entry in sorted(entries.items()):
        doi = entry.get('DOI', '').strip()
        if doi and not bi.DOI_RE.match(doi):
            problems.append(f'{slug}: {key}: malformed DOI {doi!r}')
        if not entry.get('author'):
            problems.append(f'{slug}: {key}: no author')
        if not entry.get('title'):
            problems.append(f'{slug}: {key}: no title')
        if not doi:
            warnings.append(f'{slug}: {key}: no DOI')

    try:
        _, cited, notes = bi.convert_body(
            slug, os.path.join(src, 'manuscript.tex'))
    except bi.BuildError as exc:
        problems.append(f'{slug}: {exc}')
        return

    for key in cited:
        if key in notes:
            continue  # a scientific footnote, not a bibliography entry
        if key not in entries:
            problems.append(f'{slug}: undefined citation key: {key}')
    for key in sorted(set(entries) - set(cited)):
        warnings.append(f'{slug}: {key} is never cited')


def check_generated_rst(slug, meta, problems, warnings=None):
    """The committed article must be exactly what the sources produce.

    Byte equality only means something when the same pandoc is doing the
    producing: its RST writer's output moves between versions, and CI's
    pandoc is rarely the one on the author's machine. So the generated file
    records which pandoc made it, and a mismatch downgrades this to a warning
    — otherwise every CI run after a pandoc upgrade would fail with nothing
    actually wrong. On matching versions it stays a hard failure, which is
    what keeps anyone from correcting the science in the generated file.
    """
    committed = os.path.join(bi.CONTENT, f'{slug}.rst')
    if not os.path.isfile(committed):
        problems.append(f'{slug}: content/insights/{slug}.rst has not been '
                        f'generated (run: make insight-web SLUG={slug})')
        return

    with tempfile.TemporaryDirectory() as tmp:
        try:
            fresh = bi.build_web(slug, meta, out_dir=tmp, quiet=True)
        except bi.BuildError as exc:
            problems.append(f'{slug}: {exc}')
            return
        with open(fresh, encoding='utf-8') as f:
            expected = f.read()
    with open(committed, encoding='utf-8') as f:
        actual = f.read()

    if expected != actual:
        recorded = re.search(r'Generated with pandoc (\S+?)\.', actual)
        running = bi.pandoc_version()
        if recorded and recorded.group(1) != running:
            (warnings if warnings is not None else problems).append(
                f'{slug}: content/insights/{slug}.rst was generated with '
                f'pandoc {recorded.group(1)} and this is pandoc {running}, '
                f'so it cannot be compared byte for byte. Rebuild it on one '
                f'version to check it properly.')
        else:
            problems.append(
                f'{slug}: content/insights/{slug}.rst does not match its '
                f'sources. Either it was edited by hand — which is never the '
                f'way to change an Insight — or the sources changed and it '
                f'was not rebuilt. Run: make insight-web SLUG={slug}')

    if 'DO NOT EDIT' not in actual.split('\n\n')[0]:
        problems.append(f'{slug}: generated RST has lost its DO-NOT-EDIT header')


def check_rendered_html(slug, meta, html_dir, problems):
    page = os.path.join(html_dir, 'insights', slug, 'index.html')
    if not os.path.isfile(page):
        if meta['status'] == 'published':
            problems.append(f'{slug}: published, but {page} was not built')
        return
    if meta['status'] != 'published':
        problems.append(f'{slug}: status is {meta["status"]}, but the page was '
                        f'built at insights/{slug}/')
        return

    with open(page, encoding='utf-8') as f:
        html = f.read()

    expected_url = f'https://rnaforecast.com/insights/{slug}/'
    for needle, label in [
        (f'<link rel="canonical" href="{expected_url}" />', 'canonical URL'),
        ('<meta name="description"', 'meta description'),
        ('<meta property="og:type" content="article" />', 'og:type=article'),
        ('application/ld+json', 'JSON-LD'),
    ]:
        if needle not in html:
            problems.append(f'{slug}: rendered page has no {label}')

    for field in ('title', 'subtitle'):
        value = str(meta[field])
        if value not in html:
            problems.append(f'{slug}: rendered page does not carry the '
                            f'canonical {field}: {value!r}')

    # Every cross-reference must land somewhere. A figure, table or equation
    # reference that survives conversion but loses its anchor is silent on the
    # page: it looks like a link and goes nowhere.
    ids = set(re.findall(r'\bid="([^"]+)"', html))
    for target in set(re.findall(r'href="#([^"]+)"', html)):
        if target and target not in ids:
            problems.append(f'{slug}: internal link #{target} has no target '
                            f'on the page')

    if meta.get('doi'):
        if f'doi:{meta["doi"]}' not in html:
            problems.append(f'{slug}: metadata.yaml has a DOI but the page '
                            f'shows no citation block')
    elif 'Cite this Insight' in html:
        problems.append(f'{slug}: page shows a citation block but '
                        f'metadata.yaml has no DOI')


def check(slug, html_dir, problems, warnings):
    try:
        meta = bi.load_metadata(slug)
    except bi.BuildError as exc:
        problems.append(str(exc))
        return

    check_figures(slug, problems)
    check_bibliography(slug, problems, warnings)
    check_generated_rst(slug, meta, problems, warnings)
    if html_dir:
        check_rendered_html(slug, meta, html_dir, problems)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slugs', nargs='*')
    parser.add_argument('--html', metavar='DIR',
                        help='a built site to check the rendered pages in')
    args = parser.parse_args()

    slugs = args.slugs or insight_slugs()
    if not slugs:
        print('no Insights found')
        return 0

    problems, warnings = [], []
    for slug in slugs:
        check(slug, args.html, problems, warnings)

    for warning in warnings:
        print(f'warning: {warning}')
    for problem in problems:
        print(problem)

    if problems:
        print(f'\n{len(problems)} problem(s) in {len(slugs)} Insight(s)')
        return 1
    print(f'ok: {len(slugs)} Insight(s), sources and generated files agree')
    return 0


if __name__ == '__main__':
    sys.exit(main())
