#!/usr/bin/env python3
"""Scaffold a new Insight.

    python3 scripts/new_insight.py "My New Insight"

Creates insights/<slug>/ with a manuscript, a bibliography and metadata —
placeholders only, no boilerplate prose to delete. The new Insight starts as a
draft, so it builds locally and publishes nothing.
"""

import argparse
import os
import re
import sys
import unicodedata
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSIGHTS = os.path.join(REPO, 'insights')

MANUSCRIPT = r"""% Canonical scientific source for this Insight.
%
% Body only: no \documentclass and no preamble. Scientific content only —
% website furniture (call to action, navigation, SEO) lives in the Pelican
% templates. Cite with semantic keys, never numbers: \cite{somekey}.

\begin{lead}
The opening paragraph. The website sets this as the page lead and the PDF sets
it slightly larger; it is still ordinary prose and belongs here.
\end{lead}

\section{First section}

Text.
"""

BIBLIOGRAPHY = """% Canonical bibliography. The PDF and the website both read this file.
% Mark a preprint with `pubstate = {preprint}` so both outputs say so.
"""

METADATA = """title: {title}
subtitle: A subtitle
slug: {slug}

author: Michael T. Wolfinger
# affiliation is the PDF title-page line; affiliation_formal is what a deposit
# record (Zenodo) should carry. The website says neither: it says the brand.
affiliation: RNA Forecast e.U., Purkersdorf, Vienna metropolitan area, Austria
affiliation_formal: RNA Forecast e.U., Purkersdorf, Austria

date: {today}
modified: {today}
version: "1.0"

series: RNA Forecast Insights
number: {number}

doi: null
zenodo_url: null

# license is the machine-readable value; copyright is the human statement, and
# it names a person: under Austrian law only a natural person can be an author,
# so the e.U. is publisher rather than rights holder.
license: CC BY 4.0
copyright: Copyright {year} Michael T. Wolfinger. Licensed under CC BY 4.0.
resource_type: Publication / Working paper
# Zenodo defaults this to "Zenodo", which is the archive, not the publisher.
publisher: RNA Forecast

status: draft

# Four texts, four jobs — do not make one do another's work.
# abstract: the deposit record (Zenodo) and the schema.org data. Self-contained
# and searchable: what the piece examines, on what evidence, and what it
# concludes. Required before this can be published.
abstract: >-
  A paragraph that stands on its own.

# description: the HTML meta description and search snippet. Under 150
# characters, or scripts/check_build.py fails the build.
description: >-
  One sentence for search results and link previews, under 150 characters.

# summary: the card on /insights/ and the social preview.
summary: >-
  A short paragraph for the Insights listing and for social cards.

tags:
  - RNA structure
"""


def slugify(title):
    text = unicodedata.normalize('NFKD', title)
    text = text.encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', text)).strip('-')


def next_number():
    highest = 0
    if os.path.isdir(INSIGHTS):
        import yaml
        for name in os.listdir(INSIGHTS):
            path = os.path.join(INSIGHTS, name, 'metadata.yaml')
            if not os.path.isfile(path):
                continue
            with open(path, encoding='utf-8') as f:
                meta = yaml.safe_load(f) or {}
            try:
                highest = max(highest, int(meta.get('number', 0)))
            except (TypeError, ValueError):
                pass
    return highest + 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('title')
    parser.add_argument('--slug', help='override the derived slug')
    args = parser.parse_args()

    slug = args.slug or slugify(args.title)
    if not slug:
        print('error: could not derive a slug from that title', file=sys.stderr)
        return 1

    target = os.path.join(INSIGHTS, slug)
    if os.path.exists(target):
        print(f'error: insights/{slug}/ already exists', file=sys.stderr)
        return 1

    os.makedirs(os.path.join(target, 'figures'), exist_ok=True)
    with open(os.path.join(target, 'figures', '.gitkeep'), 'w') as f:
        f.write('')
    with open(os.path.join(target, 'manuscript.tex'), 'w', encoding='utf-8') as f:
        f.write(MANUSCRIPT)
    with open(os.path.join(target, 'references.bib'), 'w', encoding='utf-8') as f:
        f.write(BIBLIOGRAPHY)
    with open(os.path.join(target, 'metadata.yaml'), 'w', encoding='utf-8') as f:
        f.write(METADATA.format(title=args.title, slug=slug,
                                today=date.today().isoformat(),
                                year=date.today().year,
                                number=next_number()))

    print(f'created insights/{slug}/')
    print(f'  edit manuscript.tex, references.bib and metadata.yaml, then:')
    print(f'    make insight SLUG={slug}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
