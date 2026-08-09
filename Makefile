PY?=python3
PELICAN?=pelican
PELICANOPTS=

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py

GITHUB_PAGES_BRANCH=gh-pages
GITHUB_PAGES_COMMIT_MESSAGE=Generate Pelican site


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
	@echo '   make publish                        generate using production settings '
	@echo '   make check                          production build + smoke tests     '
	@echo '   make validate                       Nu Html Checker over output/ (needs java)'
	@echo '   make test                           run the pytest suite              '
	@echo '   make serve [PORT=8000]              serve site at http://localhost:8000'
	@echo '   make serve-global [SERVER=0.0.0.0]  serve (as root) to $(SERVER):80    '
	@echo '   make devserver [PORT=8000]          serve and regenerate together      '
	@echo '   make devserver-global               regenerate and serve on 0.0.0.0    '
	@echo '   make github                         upload the web site via gh-pages   '
	@echo '                                                                          '
	@echo 'Set the DEBUG variable to 1 to enable debugging, e.g. make DEBUG=1 html   '
	@echo 'Set the RELATIVE variable to 1 to enable relative urls                    '
	@echo '                                                                          '

html:
	"$(PELICAN)" "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

clean:
	[ ! -d "$(OUTPUTDIR)" ] || rm -rf "$(OUTPUTDIR)"

regenerate:
	"$(PELICAN)" -r "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

# `pelican -l` only starts a server rooted at output/ — it does not build.
# Without this dependency it happily serves whatever `make check`, `make
# publish` or `make github` left behind: a production build whose absolute
# https://rnaforecast.com/... asset URLs resolve against the live site, not
# localhost, so the local preview loads no stylesheet.
serve: html
	"$(PELICAN)" -l "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

serve-global: html
	"$(PELICAN)" -l "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS) -b $(SERVER)

devserver:
	"$(PELICAN)" -lr "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

devserver-global:
	"$(PELICAN)" -lr "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS) -b 0.0.0.0

publish:
	"$(PELICAN)" "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(PUBLISHCONF)" $(PELICANOPTS)

# Production build under --fatal warnings, then smoke-test the result.
# This is what CI runs; run it locally to see what CI will see.
check:
	"$(PELICAN)" "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(PUBLISHCONF)" $(PELICANOPTS) --fatal warnings
	"$(PY)" scripts/check_build.py "$(OUTPUTDIR)"

# Nu Html Checker over the built pages. Needs a JRE. CSS checking is left off
# on purpose: the validator's stylesheet backend predates color-mix(), inset,
# aspect-ratio and nesting, and reports all of them as errors.
validate:
	html5validator --root "$(OUTPUTDIR)"

test:
	"$(PY)" -m pytest

# Manual fallback publish. CI deploys from main; this pushes the gh-pages
# branch directly, and still refuses to ship a build that fails the checks.
github: check
	ghp-import -m "$(GITHUB_PAGES_COMMIT_MESSAGE)" -b $(GITHUB_PAGES_BRANCH) "$(OUTPUTDIR)" --no-jekyll
	git push origin $(GITHUB_PAGES_BRANCH)


.PHONY: html help clean regenerate serve serve-global devserver devserver-global publish check validate test github
