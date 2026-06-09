# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static website for RNA Forecast (rnaforecast.com), a biotechnology consultancy. Built with **Pelican** (Python static site generator) using a custom **m.css** Material Design theme.

## Build Commands

```bash
# Development build
make html

# Serve locally (port 8000)
make serve

# Auto-rebuild on file changes + serve
make devserver

# Production build (uses publishconf.py, sets absolute URLs + analytics)
make publish

# Build and push to gh-pages branch
make github

# Remove output directory
make clean
```

## Architecture

### Configuration Split

- `pelicanconf.py` — development config; relative URLs, OSANO cookie consent disabled, no analytics
- `publishconf.py` — extends pelicanconf.py for production; sets `SITEURL=https://rnaforecast.com`, enables Google Analytics (G-XDJC7M3EQS), enables OSANO consent, enables `DELETE_OUTPUT_DIRECTORY`

### Content

All pages live in `content/pages/` as reStructuredText (`.rst`). The site has four pages: index, research, contact, legal. Pages use Pelican metadata headers and custom m.css roles/directives for components (hero sections, CTAs, cards).

### Theme & CSS Pipeline

The theme in `pelican-theme/` uses the m.css framework. Custom stylesheets are in `content/css/`:

- `m-rnaf-layout.css` + `m-rnaf-components.css` + `m-rnaf-light.css` — source files
- `m-rnaf.compiled.css` — **compiled output**, the file actually served; do not edit directly
- `postprocess.py` + `pp_rnaf.sh` — CSS post-processor/minifier; run `./content/css/pp_rnaf.sh` after editing source CSS files to regenerate the compiled CSS

The compiled CSS is committed to the repo. When modifying styles, edit the source files and regenerate `m-rnaf.compiled.css`.

### Plugins

Custom plugins in `plugins/m/` provide m.css integration:
- `htmlsanity.py` — HTML sanitization and formatting
- `components.py` — m.css component directives (panels, grid, etc.)
- `images.py` — responsive image handling
- `link.py` — link processing

`plugins/sitemap.py` generates the XML sitemap.

### Deployment

GitHub Actions (`static.yml`) deploys the `gh-pages` branch to GitHub Pages on push to `main`. The workflow deploys the repository as-is (no build step in CI) — the `output/` directory is pre-built locally and pushed via `make github` / `inv gh-pages` (uses `ghp-import`).

`gh-pages` is always fully regenerated, so force-push is required: use `git push origin gh-pages -f` if `make github` fails due to a diverged remote.

### URL Structure

Pages are output as `{slug}/index.html` (directory-style URLs), configured via `PAGE_URL = '{slug}/'` and `PAGE_SAVE_AS = '{slug}/index.html'` in pelicanconf.py.
