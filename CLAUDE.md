# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static website for RNA Forecast (rnaforecast.com), Michael T. Wolfinger's
independent research platform for computational RNA biology. Built with
**Pelican** (Python static site generator) on a custom theme implementing the
"Industry" design system.

**The site ships no JavaScript.** Every interaction — the mobile navigation, all
hover and focus states — is CSS only. The only `<script>` in a development build
is the JSON-LD block, which is structured data for search engines, not code.
A production build adds the consent gate from `base.html` — the Consent Mode
defaults, the Google tag, and the bridge that hands Osano's decision to it —
plus their two external scripts. `scripts/check_build.py` allows exactly those
and fails on anything else. Do not introduce client-side scripting.

## Packaging

`pyproject.toml` (setuptools, `py-modules = []` — this is a source repository,
not an importable library) declares the dependencies. Install with
`pip install -e ".[dev,test]"`. `docutils` carries an upper bound because it is
the RST writer and a minor bump changes the generated HTML; nothing else is
pinned tightly. Requires Python 3.13, matching the michaelwolfinger.com repo.

`tests/` is a pytest suite. `tests/conftest.py` runs one production build per
session into a temporary directory; `test_build.py` and `test_seo.py` assert
against it, `test_scholarly.py` unit-tests the structured-data extractor
against both publication layouts, and `test_checker.py` injects each fault
class into a copy of the build to prove `scripts/check_build.py` still catches
it. `plugins/` and `scripts/` are imported as namespace packages via
`pythonpath = ["."]`.

## Build Commands

```bash
make html       # development build
make serve      # serve locally on port 8000
make devserver  # auto-rebuild on change + serve
make publish    # production build into output-publish/ (absolute URLs, analytics)
make check      # what CI runs: production build --fatal warnings + smoke tests
make validate   # Nu Html Checker over output-publish/ (needs a JRE)
make test       # pytest suite
make clean      # remove both output dirs
```

## Architecture

### Configuration split

- `pelicanconf.py` — development; relative URLs, no analytics, `OSANO = False`
- `publishconf.py` — production; sets `SITEURL`, enables Google Analytics and OSANO

Navigation, footer and the site logo are data, not markup:

```python
M_LINKS_NAVBAR1 = [('Label', '/url/', 'slug')]  # slug marks the current page
R_FOOTER_TAGLINE = "..."
R_FOOTER_LINKS = [('Label', '/url/')]
R_FOOTER_PROFILES = [('Label', 'https://...')]  # external, rel="me noopener"
```

`FORMATTED_FIELDS` lists the page metadata fields whose value is
reStructuredText and must reach the template as rendered HTML
(`hero_links`, `hero_actions`, `hero_body`).

### Content

Six pages in `content/pages/` as reStructuredText: index, research,
publications, about, impressum, datenschutz — plus `thanks` and `404`, which
are only reached by being sent there. There is no blog; `ARTICLE_PATHS` points
at a directory that does not exist to keep the article generator quiet.

`impressum` is the Austrian § 25 MedienG disclosure — media owner, address,
responsible for content, editorial policy — and `datenschutz` is the GDPR
privacy notice. They are two pages on purpose: the imprint has to stay short
and unmistakable. Both carry a private residential address, so both are
`Disallow`ed in `robots.txt`, excluded from the sitemap and declared out of
scope in `llms.txt`; `EXCLUDED_PATHS` and `EXCLUDED_SLUGS` in
`scripts/check_build.py` are what keep those three files agreeing. Both use
`:page_class: legal`, which is the "reads as a document" style, not a page
name. There is no `/legal/` URL.

Page metadata drives the hero; the body is ordinary RST:

```rst
:hero_kicker:        small label above the title
:hero_title:         the page's <h1>
:hero_sub:           subtitle line (home page only; its presence selects the tall hero)
:hero_links:         a run of links, RST
:hero_lead:          the lead paragraph
:hero_actions:       a run of links rendered as buttons; the first is primary
:hero_portrait:      image path — switches the hero to the portrait layout (about)
:hero_body:          multi-paragraph RST for the portrait hero
:page_class:         extra class on <main> (impressum, datenschutz)
```

Use **anonymous** hyperlink references (double underscore, ``` `text <url>`__ ```)
in metadata and in link rows. A named reference creates an implicit target, which
collides with section ids elsewhere in the same document and produces suffixed
ids like `software-1`.

### Writing content against the design

reStructuredText can emit a class but never an inline style, an id, or a
`data-` attribute. The stylesheet is built around that:

- **Prose needs no classes.** Element defaults style `p`, `h2`, `ul`, `figure`,
  `table` and friends, so a plain page already looks finished.
- **Components are one wrapper, one class**: `.. container:: blueprint glance`.
  Children are styled by descendant and child selectors, never by their own class.
- **Section labels.** A top-level section gets a two-digit counter above a rule
  automatically. To label it in words instead, add `.. container:: kicker` inside
  the section — CSS `order` hoists it above the heading. On pages where the label
  *is* the heading, put `.. class:: labelled` before the section title.
- **Section ids** come from `.. _name:` before the title, which docutils renders
  as an anchor span inside the section.
- **Links take their look from their row**: `.. container:: actions` (ghost),
  `actions-primary` (solid), `hero-actions` (first solid, rest outlined),
  `tag-row` (tag-shaped). There is no way to class an inline link.
- **Headings inside a container** are not possible; use `.. container:: card-h`,
  `collab-h`, `subsection-h`, `pub-title` and similar named containers.

### Theme

`pelican-theme/templates/` holds exactly two templates: `base.html` (document
shell, masthead, footer) and `page.html` (hero variants, article). The masthead's
mobile drawer is a checkbox plus `:checked ~` selectors.

`plugins/m/htmlsanity.py` is the only m.css remnant, kept for its clean HTML5
writer (`<section>`, `<figure>`, unprefixed container classes) and the
`format_siteurl` / `render_rst` Jinja filters. It is load-bearing, not
optional: without it the templates fail on the first `format_siteurl` call and
the generated markup no longer matches the stylesheet. It is a *writer*, not a
validator — `make validate` does the checking.

`plugins/sitemap.py` writes the sitemap. `plugins/scholarly.py` derives
schema.org `ScholarlyArticle` data from the publication markup Pelican has
already rendered, and hands it to the template as `page.jsonld`. Deriving it
from the page rather than a parallel data file means the bibliography cannot
drift from the prose; it reads both publication layouts (the full listing on
`/publications/`, the compact one on the home page).

### CSS

`content/css/rnaf.css` is the whole stylesheet — one plain file, no build step,
no preprocessor, served as-is. It is organised in five layers: tokens, base
elements, design-system components, site components, responsive and print.

Take every value from a token (`var(--color-*)`, `--space-*`, `--ink-*`,
`--shell-*`). Do not hard-code a hex below `:root`.

Two things worth knowing before editing:

- The blueprint frame's four `+` registration marks are drawn as eight
  background gradients on `.blueprint::before`. The design used four child
  elements, which RST cannot produce.
- Fixed grid columns must be `minmax(0, 1fr)`, and any explicit `grid-column`
  needs releasing in the mobile breakpoint, or the grid keeps its second column.

Fonts (Barlow, Barlow Condensed) are self-hosted in `content/static/fonts/`.
The site makes **no third-party requests** — it runs behind a cookie consent
banner, so a font CDN would be exactly what that banner exists to gate.

### Deployment

CI builds and publishes. `.github/workflows/build-deploy.yml` installs the
package with `pip install -e ".[dev,test]"`, runs `make test`, `make check` and
`make validate`, and deploys `output-publish/` to Pages as an artifact. Push to
`main` publishes; pull requests build and check but never deploy.

**Push to `main` is the only publish path.** There is no `gh-pages` branch and
no manual target — Pages is set to build type "GitHub Actions", so a branch
push would not reach the site anyway. Do not reintroduce a `ghp-import` step:
under this setting it succeeds, reports nothing wrong, and changes nothing.

**Cloudflare sits in front of GitHub Pages** — the apex record is proxied, so
every request is answered at the edge first. Three consequences worth knowing.
One redirect lives there and nowhere in this repository: `/legal` and `/legal/`
→ `https://rnaforecast.com/impressum/`, a 301 Single Redirect Rule, left over
from the page's old URL. DNS is there too, so the Search Console verification
record is a Cloudflare TXT entry rather than anything in the build. And
Cloudflare can inject JavaScript into the served
HTML at the edge — Bot Fight Mode and Cloudflare Web Analytics both do — which
`check_build.py` cannot see, because it reads the build on disk and never the
served page. Both must stay off, or the site stops being JavaScript-free
without anything in CI noticing.

The two builds never share a directory: `make html`/`serve` write the
development build to `output/`, `make publish`/`check`/`validate` write the
production build to `output-publish/`. Sharing one directory left absolute
`https://rnaforecast.com/…` URLs where the local server expected relative
ones, so the preview pointed at the live site.

`make check` is the gate: a production build under `--fatal warnings`, then
`scripts/check_build.py`. That script verifies the expected pages exist, that
every reference to the site's own files resolves (including absolute
`https://rnaforecast.com/…` links), that `CNAME` is intact, that no page
requests anything from a host outside analytics and the consent banner, that
every `url()` in the stylesheet resolves (the self-hosted fonts are referenced
from nowhere else), that the contact form still posts only to its declared
endpoint — a form action is a data flow, and the disclosure in the privacy
notice has to keep matching it — that every JSON-LD block parses and the publication
graph covers every paper and DOI on the page, that the share card is present at
1200×630, and that `robots.txt`, the sitemap and its exclusions agree with the
pages on disk.
Run it locally to see what CI will see. Its `REQUIRED` list names the pages
the site must publish — update it when adding or retiring a page.

`make validate` runs the Nu Html Checker over the built pages and needs a JRE.
CSS checking is deliberately off: the validator's stylesheet backend predates
`color-mix()`, `inset`, `aspect-ratio` and nesting and reports every use of
them as an error.

### SEO and machine readers

AI crawlers are allowed on purpose: `content/extra/robots.txt` names the search,
answer-engine and model-training agents explicitly, so access is a decision on
record rather than a default. It also carries the `Sitemap:` line.
`content/extra/llms.txt` is the site summary for LLM consumers; keep it in step
when a page is added or retired.

Structured data is all emitted by `plugins/scholarly.py`, one JSON-LD block per
page. The site's own identity lives in `R_SITE_GRAPH` in `pelicanconf.py` as
data, not as a raw HTML block in `index.rst`: any `@id` or `url` there starting
with `#` or `/` gets `SITEURL` prefixed at build time. That is what keeps the
production domain out of a local preview — a development build contains no
`rnaforecast.com` anywhere except the contact form's `_next` field, which
FormSubmit requires to be absolute. Keep `#michael-t-wolfinger` in
`R_SITE_GRAPH` in step with `AUTHOR_FRAGMENT` in the plugin, or the site graph
and the publication graph will describe two different people.

**The consent gate in `base.html` is order-dependent and must not be
rearranged**: Consent Mode defaults (everything denied) first, then the Osano
script, then the Google tag. Defaults after the tag means gtag.js sets its
cookies before anyone is asked, and a CMP loaded after the tracker cannot block
it. `check_build.py` asserts this ordering. `GOOGLE_SITE_VERIFICATION` in
`pelicanconf.py` emits the Search Console meta tag when set; it is empty by
default because DNS verification is the better option — a TXT record in
Cloudflare, on a domain property, which covers every scheme and subdomain at
once and cannot be broken by a change to the pages.

Search Console is independent of Google Analytics and survives its removal, but
the *verification* may not: GA4's `gtag.js` is itself an accepted verification
method, and with no meta tag, no HTML verification file and no TXT record in
place, that is what a property here would be resting on. Check Settings →
Ownership verification and get a DNS record verified **before** removing the
Google tag, or the property un-verifies.

`M_SOCIAL_IMAGE` points at `static/images/og-card.png`, 1200×630. Every page
declares `twitter:card=summary_large_image`, so that file must exist at that
size or the checker fails.

### URL structure

Directory-style: `PAGE_URL = '{slug}/'`, `PAGE_SAVE_AS = '{slug}/index.html'`.
The former `/contact/` page is retired; contact now lives at `/about/#contact`.

### Design source

`RNAF2026/` holds the original design-canvas output the site was converted from
(`*.dc.html`, the `_ds/` design-system bundle, `responsive.css`). It is reference
material, not part of the build.
