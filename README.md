# rnaforecast.com

Pelican source repository for [rnaforecast.com](https://rnaforecast.com), the
independent research platform of Michael T. Wolfinger for computational RNA
biology.

The site is static, self-hosts its fonts, makes no third-party requests beyond
analytics and the consent banner that gates it, and ships no JavaScript of its
own.

## Install

```bash
python3.13 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev,test]"
```

`make validate` additionally needs a JRE on `PATH` for the Nu Html Checker.

## Commands

```bash
make html       # development build
make serve      # serve locally on port 8000
make devserver  # auto-rebuild on change + serve
make publish    # production build into output-publish/ (absolute URLs, analytics)
make check      # what CI runs: production build --fatal warnings + smoke tests
make validate   # Nu Html Checker over output-publish/
make test       # pytest suite
make clean      # remove both output dirs
```

## Layout

| path | what it is |
|---|---|
| `content/pages/` | the pages, as reStructuredText |
| `content/css/rnaf.css` | the whole stylesheet, no build step |
| `content/extra/` | `robots.txt`, `llms.txt`, `CNAME`, favicons, touch icon, web manifest |
| `pelican-theme/templates/` | `base.html` and `page.html` |
| `plugins/` | the RST writer, the sitemap, the publication structured data |
| `scripts/check_build.py` | smoke tests over a built site |
| `tests/` | pytest suite |
| `RNAF2026/` | original design-canvas output; reference, not part of the build |

## Deployment

Push to `main`. That is the only way the site is published: GitHub Actions
builds, checks, validates and uploads to GitHub Pages. Pull requests build and
check but never deploy. There is no `gh-pages` branch and no manual publish
path.
