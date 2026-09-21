# RNA Forecast Insights — authoring workflow

An Insight is written once, in LaTeX, and published twice: as an archival PDF
for Zenodo and as a page on rnaforecast.com. Both come from the same three
files, so the two cannot drift apart.

```
insights/<slug>/manuscript.tex     prose, headings, citations, figures
insights/<slug>/references.bib     the only bibliography
insights/<slug>/metadata.yaml      title, date, version, DOI, status
insights/<slug>/figures/
         │
         ├──> build/insights/<slug>/<slug>.pdf   archival PDF, for Zenodo
         └──> content/insights/<slug>.rst        generated, committed
                       └──> Pelican ──> https://rnaforecast.com/insights/<slug>/
```

**`content/insights/<slug>.rst` is a build artifact.** It carries a
DO-NOT-EDIT header, and CI regenerates it and fails if the committed file
differs. To change a word of science, edit the manuscript and rebuild. There is
no reverse path.

## Create an Insight

```bash
make new-insight TITLE="The Title Of The Piece"
```

This writes `insights/<slug>/` with empty placeholders and `status: draft`.

## Edit an Insight

Decide where a change belongs before making it:

| The change affects | Edit |
| --- | --- |
| wording, claims, headings, citation placement, equations, captions | `manuscript.tex` |
| an author, title, journal, year, volume, pages, DOI, publication type | `references.bib` |
| public title, subtitle, date, version, DOI, summary, tags, draft/published | `metadata.yaml` |
| navigation, cards, the service CTA, layout, SEO, JSON-LD, Open Graph | `pelican-theme/templates/`, `content/css/rnaf.css` |
| the PDF title page, PDF typography, series branding | `insights/templates/insight.tex` |

Cite with semantic keys — `\cite{mccaskill1990}`, or `\cite{a,b}` for several
at one place. Never write a reference number: both outputs number in order of
first citation, and moving a paragraph renumbers everything downstream.

Mark a preprint in the `.bib` with `pubstate = {preprint}`. The PDF then prints
`[Preprint]` and the website prints `Preprint.`, so a preprint is never
mistaken for a peer-reviewed paper.

Two `.bib` conventions matter, because titles are stored in sentence case and
re-capitalised on the way out:

- protect a word that must keep its capitals with braces — `{RNA}`, `{NNDB}`,
  `{mRNA}`;
- for an italic species name, brace the whole command:
  `{\emph{Escherichia coli}}`. Written as `\emph{{Escherichia coli}}` it comes
  back lower-cased.

Two environments carry meaning rather than formatting, and exist in both
outputs: `lead` (the opening paragraph) and `chain` (the conceptual sequence,
an `enumerate` inside it). Any other LaTeX environment becomes a CSS container
of the same name on the website — `\begin{foo}` gives `.. container:: foo` —
so a new one needs a matching rule in `content/css/rnaf.css`.

## The four texts

An Insight carries four pieces of prose that are easy to confuse. Each has one
job, and none of them should be made to do another's:

| Text | Lives in | Goes to | Shape |
| --- | --- | --- | --- |
| `abstract` | `metadata.yaml` | the Zenodo record and the page's schema.org `abstract` | self-contained paragraph: what the piece examines, on what evidence, what it concludes. Never printed on the page |
| `description` | `metadata.yaml` | `<meta name="description">`, the search snippet | one sentence, **under 150 characters** or `check_build.py` fails |
| `summary` | `metadata.yaml` | the card on `/insights/`, Open Graph | a few sentences, written to make someone open the article |
| `lead` | `\begin{lead}` in `manuscript.tex` | the article's opening paragraph, and the PDF | written to be read, not indexed |

The abstract is required before an Insight can be `status: published`, because
every published Insight is deposited. It is deliberately kept off the page: the
article already opens with its lead, and printing both says the same thing
twice in different words.

One trap worth knowing: the generated `.rst` writes it as `:bib_abstract:`,
not `:abstract:`. docutils reserves `abstract` as a bibliographic field, turns
it into a topic in the document body and never hands it to Pelican — so the
abstract would appear above the lead and be missing from the structured data.

## Affiliation

Three layers, deliberately worded differently, all from `metadata.yaml`:

| Where | Value | Why |
| --- | --- | --- |
| PDF title page (`affiliation`) | `RNA Forecast e.U., Purkersdorf, Vienna metropolitan area, Austria` | the registered entity and its seat, with enough geography for an international reader |
| Zenodo record (`affiliation_formal`) | `RNA Forecast e.U., Purkersdorf, Austria` | a deposit record should name the registered seat and nothing more |
| Website | `RNA Forecast` | branding; the legal detail lives in `/impressum/` |

Purkersdorf is not administratively part of Vienna, so no layer says it is.
`make insight-pdf` prints the Zenodo value after the build, ready to paste
into the deposit form.

## Rights

`license` is the machine-readable value — the deposit's licence selector and
the page's schema.org `license`. `copyright` is the human statement, and it
appears on the PDF title page in place of the bare licence, which it already
names:

    Copyright 2026 Michael T. Wolfinger. Licensed under CC BY 4.0.

It names a natural person on purpose. Austrian copyright follows the droit
d'auteur model — only a person can be an author (§ 10 UrhG) — so RNA Forecast
e.U. is the publisher and the affiliation, never the rights holder.

`resource_type` records what was chosen in the deposit form (`Publication /
Working paper`) so the record and this file cannot drift.

CC BY on Zenodo is irrevocable: a later version can be deposited, but the
licence on a published record cannot be withdrawn. Every figure has to be
yours or compatibly licensed before the first deposit, because the licence
covers the whole upload.

## PDF typography

The PDF is set in **Source Sans Pro**, a neutral sans designed for continuous
text, with headings in its semibold weight — matching the website, where
`--font-heading-weight` is 600. Barlow itself cannot be used: it is not in TeX
Live, and the files in `content/static/fonts/` are woff2 subsets, which LaTeX
cannot read, so the two faces are relatives rather than the same font.

The font is one clearly marked block near the top of
`insights/templates/insight.tex`. Alternatives already installed, all
pdflatex-ready: `roboto` (closest in shape to Barlow, and the only one here
with a condensed cut), `FiraSans` (warm, humanist), `inter` (modern,
screen-first), `lato`, `opensans`. Swapping is a one-line change, but
`\headingfont` has to name a weight the new face actually has.

Maths comes from `newtxsf` so that a Δ or a Greek letter matches the text
face instead of arriving in Computer Modern.

## Build

```bash
make insight SLUG=<slug>        # PDF and website article
make insight-web SLUG=<slug>    # website only (needs pandoc)
make insight-pdf SLUG=<slug>    # PDF only (needs a LaTeX toolchain)
make insights                   # rebuild every Insight for the web
make html && make serve         # look at it
```

## Validate

```bash
make insight-check              # every Insight
make insight-check SLUG=<slug>  # one
make check                      # the full site, this included
```

`check_insight.py` fails on an undefined citation key, a missing figure, a
duplicate or malformed bibliography entry, incomplete metadata on something
marked published, and — the important one — a committed `.rst` that does not
match what the sources produce. It warns about a reference that is never cited
and about an entry with no DOI.

## Publish

1. Finish the manuscript and validate it.
2. Start a Zenodo draft and click **Reserve DOI** — do not upload anything
   yet. The draft will show a red error on Files; that is a publish-time
   check, and a draft saves without files. The point of reserving is to get
   the DOI *into* the PDF, and Zenodo freezes files at publish, so a PDF
   uploaded before the DOI exists can only be corrected by a new version.
   Keep the same draft: the reserved DOI belongs to it.
3. Put it in `metadata.yaml` as `doi:` — bare, no `https://doi.org/` — and set
   `status: published`. Use the *version* DOI that Reserve gives you, not the
   concept DOI Zenodo derives afterwards: the PDF should identify the exact
   artifact deposited.
4. `make insight SLUG=<slug>` — both outputs now carry the DOI.
5. `make check && make test`.
6. Upload `build/insights/<slug>/<slug>.pdf` to Zenodo. The fields to paste —
   title, author with the formal affiliation, date, version, licence,
   keywords, the related identifier and the abstract — are written next to it
   as `build/insights/<slug>/zenodo.txt`, so nothing is retyped.
7. Commit and push. Pushing to `main` is what publishes the website.

A draft never reaches production: `DRAFT_SAVE_AS` is empty, so no page, no
sitemap entry and no listing.

## Versions

`version` in `metadata.yaml` appears on the PDF and in the page byline.

- typo or a website-only fix: leave it alone;
- a clarification that does not change the interpretation: bump the minor;
- changed argument, interpretation or references that affect a claim: bump the
  major, and deposit a new Zenodo version rather than overwriting the old one.

## Tooling

`pandoc` for the website build, `latexmk` with a LaTeX distribution and
`bibtex` for the PDF, Python with PyYAML for the wrapper. CI installs only
pandoc: it regenerates the `.rst` to prove nobody edited it, and never builds
the PDF.
