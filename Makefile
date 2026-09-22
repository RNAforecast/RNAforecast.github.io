PY?=python3
PELICAN?=pelican
PELICANOPTS=

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
# The production build goes somewhere else on purpose. Sharing one directory
# means `make check` leaves absolute rnaforecast.com URLs where the local
# server expects a development build, and the preview silently points at the
# live site.
PUBLISHDIR=$(BASEDIR)/output-publish
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py


DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += -D
endif

RELATIVE ?= 0
ifeq ($(RELATIVE), 1)
	PELICANOPTS += --relative-urls
endif

SERVER ?= "0.0.0.0"

PORT ?= 0
ifneq ($(PORT), 0)
	PELICANOPTS += -p $(PORT)
endif


help:
	@echo 'Makefile for a pelican Web site                                           '
	@echo '                                                                          '
	@echo 'Usage:                                                                    '
	@echo '   make html                           (re)generate the web site          '
	@echo '   make clean                          remove the generated files         '
	@echo '   make regenerate                     regenerate files upon modification '
	@echo '   make publish                        production build into output-publish/'
	@echo '   make check                          production build + smoke tests     '
	@echo '   make validate                       Nu Html Checker over output/ (needs java)'
	@echo '   make test                           run the pytest suite              '
	@echo '   make insight SLUG=<slug>            build one Insight: PDF + website  '
	@echo '   make insight-check SLUG=<slug>      validate an Insight               '
	@echo '   make insight-deposit SLUG=<slug>    check the served PDF against Zenodo'
	@echo '   make insights                       rebuild every Insight for the web '
	@echo '   make new-insight TITLE="..."        scaffold a new Insight            '
	@echo '   make serve [PORT=8000]              serve site at http://localhost:8000'
	@echo '   make serve-global [SERVER=0.0.0.0]  serve (as root) to $(SERVER):80    '
	@echo '   make devserver [PORT=8000]          serve and regenerate together      '
	@echo '   make devserver-global               regenerate and serve on 0.0.0.0    '
	@echo '                                                                          '
	@echo 'Set the DEBUG variable to 1 to enable debugging, e.g. make DEBUG=1 html   '
	@echo 'Set the RELATIVE variable to 1 to enable relative urls                    '
	@echo '                                                                          '

html:
	"$(PELICAN)" "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

clean:
	[ ! -d "$(OUTPUTDIR)" ] || rm -rf "$(OUTPUTDIR)"
	[ ! -d "$(PUBLISHDIR)" ] || rm -rf "$(PUBLISHDIR)"

regenerate:
	"$(PELICAN)" -r "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

# `pelican -l` serves output/ without building it. Without this dependency it
# serves whatever `make check` left behind — a production build whose absolute
# URLs resolve against the live site, so the preview loads no stylesheet.
serve: html
	"$(PELICAN)" -l "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

serve-global: html
	"$(PELICAN)" -l "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS) -b $(SERVER)

devserver:
	"$(PELICAN)" -lr "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

devserver-global:
	"$(PELICAN)" -lr "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS) -b 0.0.0.0

publish:
	"$(PELICAN)" "$(INPUTDIR)" -o "$(PUBLISHDIR)" -s "$(PUBLISHCONF)" $(PELICANOPTS)

check:
	"$(PELICAN)" "$(INPUTDIR)" -o "$(PUBLISHDIR)" -s "$(PUBLISHCONF)" $(PELICANOPTS) --fatal warnings
	"$(PY)" scripts/check_build.py "$(PUBLISHDIR)"
	"$(PY)" scripts/check_insight.py --html "$(PUBLISHDIR)"

# --- Insights ------------------------------------------------------------
# LaTeX is the scientific source; the .rst under content/insights/ and the PDF
# under build/ are both generated from it. Never edit the generated .rst.
#
#   make insight SLUG=<slug>        PDF + website article
#   make insight-web SLUG=<slug>    website article only (needs pandoc)
#   make insight-pdf SLUG=<slug>    archival PDF only (needs LaTeX)
#   make insight-check SLUG=<slug>  validate sources and generated files
#   make insight-deposit SLUG=<slug> served PDF vs the Zenodo record (network)
#   make insights                   rebuild every Insight
#   make new-insight TITLE="..."    scaffold a new one

insight:
	@[ -n "$(SLUG)" ] || { echo 'usage: make insight SLUG=<slug>'; exit 2; }
	"$(PY)" scripts/build_insight.py "$(SLUG)"

insight-web:
	@[ -n "$(SLUG)" ] || { echo 'usage: make insight-web SLUG=<slug>'; exit 2; }
	"$(PY)" scripts/build_insight.py "$(SLUG)" --web

insight-pdf:
	@[ -n "$(SLUG)" ] || { echo 'usage: make insight-pdf SLUG=<slug>'; exit 2; }
	"$(PY)" scripts/build_insight.py "$(SLUG)" --pdf

insight-check:
	"$(PY)" scripts/check_insight.py $(SLUG)

# Reaches the network: the served PDF and its metadata against the Zenodo
# record the DOI names. Run it after depositing a version, not in CI.
insight-deposit:
	"$(PY)" scripts/check_insight.py $(SLUG) --deposit

# An Insight is a directory with a metadata.yaml in it — not every entry under
# insights/, which also holds the templates and the README.
insights:
	@for meta in insights/*/metadata.yaml; do \
	  [ -f "$$meta" ] || continue; \
	  slug=$$(basename $$(dirname "$$meta")); \
	  "$(PY)" scripts/build_insight.py "$$slug" --web || exit 1; \
	done

new-insight:
	@[ -n "$(TITLE)" ] || { echo 'usage: make new-insight TITLE="My New Insight"'; exit 2; }
	"$(PY)" scripts/new_insight.py "$(TITLE)"

# Needs a JRE. CSS checking is off on purpose: the validator's stylesheet
# backend predates color-mix(), inset, aspect-ratio and nesting.
validate:
	html5validator --root "$(PUBLISHDIR)"

test:
	"$(PY)" -m pytest


.PHONY: html help clean regenerate serve serve-global devserver devserver-global publish check validate test insight insight-web insight-pdf insight-check insights new-insight insight-deposit
