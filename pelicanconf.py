DELETE_OUTPUT_DIRECTORY = True
AUTHOR = 'Michael T. Wolfinger'
SITENAME = 'RNA Forecast'
SITEURL = ""

PATH = "content"

TIMEZONE = 'Europe/Vienna'

DEFAULT_LANG = 'en'

THEME = 'pelican-theme'
THEME_STATIC_DIR = 'static'
DIRECT_TEMPLATES = []

# Insights are Pelican articles under the hood; the public wording is always
# "Insights", never "blog". The landing page at /insights/ is an ordinary
# Pelican page (content/pages/insights.rst) that iterates the article list,
# so it keeps the site's hero, metadata and sitemap handling.
ARTICLE_PATHS = ['insights']
ARTICLE_URL = 'insights/{slug}/'
ARTICLE_SAVE_AS = 'insights/{slug}/index.html'

# Drafts are not written at all: an unlisted URL is still a published URL.
# Pelican's writer skips an empty save_as.
DRAFT_URL = ''
DRAFT_SAVE_AS = ''

# Tags and categories stay in the source as metadata, but a handful of
# articles cannot fill a taxonomy: those pages would be thin and duplicate.
# Emptying CATEGORY_SAVE_AS also stops Pelican assigning a category at all,
# and its draft writer reads one — hence the default here, which is never
# rendered: no template prints it and no URL contains it.
DEFAULT_METADATA = {'category': 'Insights'}
CATEGORY_SAVE_AS = ''
CATEGORY_URL = ''
TAG_SAVE_AS = ''
TAG_URL = ''
AUTHOR_SAVE_AS = ''
AUTHOR_URL = ''

DEFAULT_DATE_FORMAT = '%-d %B %Y'

# Fingerprinted with the stylesheet's own content. Cloudflare caches the CSS
# at the edge for hours, so without this a deploy ships new HTML against the
# previous stylesheet and the site renders unstyled until the cache expires —
# which is exactly what happened when Insights first went live. A new digest
# is a URL the edge has never seen, so it fetches it; an unchanged stylesheet
# keeps its URL and stays cached.
def _fingerprint(path):
    import hashlib
    import os
    full = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'content', path.lstrip('/'))
    with open(full, 'rb') as f:
        return f'{path}?v={hashlib.sha256(f.read()).hexdigest()[:10]}'


M_CSS_FILES = [_fingerprint('/css/rnaf.css')]

FORMATTED_FIELDS = ['summary', 'hero_links', 'hero_actions', 'hero_body']

M_THEME_COLOR = '#5980a6'

PLUGIN_PATHS = ['plugins']
PLUGINS = ['m.htmlsanity',   # the HTML5 RST writer the whole stylesheet targets
           'semantics',      # headings and lang, which RST cannot express
           'scholarly',      # schema.org data derived from the publications page
           'sitemap']

M_FAVICON = ('favicon.ico', 'image/x-icon')

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

M_SITE_LOGO = 'static/images/rnaforecast-logo.svg'
# The logo's intrinsic ratio, from the SVG's viewBox. The stylesheet sets the
# height and leaves the width automatic, so without these the masthead reflows
# once the SVG has loaded.
M_SITE_LOGO_SIZE = (2526, 750)
M_SOCIAL_TWITTER_SITE = '@mtwolfinger'

# 1200x630, the size every share consumer expects. Raster only; none render SVG.
M_SOCIAL_IMAGE = 'static/images/og-card.png'

# (label, url, slug) — slug marks the current page. No 'Home': the wordmark
# links home, and its aria-label in base.html is what announces that.
M_LINKS_NAVBAR1 = [('Research', '/research/', 'research'),
                   ('Publications', '/publications/', 'publications'),
                   ('Insights', '/insights/', 'insights'),
                   ('Software', '/#software', ''),
                   ('Collaborations', '/#collaborations', ''),
                   ('Teaching & Training', '/#training', ''),
                   ('About', '/about/', 'about'),
                   ('Contact', '/#contact', '')]

R_FOOTER_TAGLINE = ('Independent research platform · Computational RNA biology '
                    '· Purkersdorf / Vienna, Austria')

R_FOOTER_LINKS = [('Home', '/'),
                  ('Research', '/research/'),
                  ('Publications', '/publications/'),
                  ('Insights', '/insights/'),
                  ('Teaching', '/#training'),
                  ('About', '/about/'),
                  ('Impressum', '/impressum/'),
                  ('Privacy', '/datenschutz/')]

R_FOOTER_PROFILES = [('GitHub', 'https://github.com/mtw'),
                     ('ORCID', 'https://orcid.org/0000-0003-0925-5205'),
                     ('Google Scholar',
                      'https://scholar.google.at/citations?user=w0PHGnEAAAAJ&hl=en')]

STATIC_PATHS = ['static', 'extra', 'css', 'files']
# Everything under STATIC_PATHS is copied as-is, so a Finder .DS_Store in a
# working copy would ship. The build checker refuses dotfiles and scripts.
IGNORE_FILES = ['.#*', '.DS_Store']
EXTRA_PATH_METADATA = {
    'extra/robots.txt': {'path': 'robots.txt'},
    'extra/favicon.ico': {'path': 'favicon.ico'},
    'extra/CNAME': {'path': 'CNAME'},
    'extra/llms.txt': {'path': 'llms.txt'},
}

PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

# Each Insight's archival PDF, published beside the article it belongs to.
# Google Scholar follows a citation_pdf_url only when the PDF sits "in the
# same subdirectory as the HTML abstract", so /static/… would not do: the file
# is kept under content/static/insights/<slug>/ and written out to
# insights/<slug>/<slug>.pdf. `make insight-pdf` puts it there.
def _insight_pdfs():
    import glob
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    found = {}
    for pdf in sorted(glob.glob(os.path.join(here, 'content', 'static',
                                             'insights', '*', '*.pdf'))):
        slug = os.path.basename(os.path.dirname(pdf))
        if os.path.basename(pdf) == f'{slug}.pdf':
            found[slug] = os.path.relpath(pdf, os.path.join(here, 'content'))
    return found


INSIGHT_PDFS = _insight_pdfs()
for _slug, _source in INSIGHT_PDFS.items():
    EXTRA_PATH_METADATA[_source] = {'path': f'insights/{_slug}/{_slug}.pdf'}

# Data, not markup, so the domain is not baked into content: any "@id" or
# "url" starting with "#" or "/" gets SITEURL prefixed at build time, which
# keeps rnaforecast.com out of a local preview. Keep "#michael-t-wolfinger"
# in step with AUTHOR_FRAGMENT in plugins/scholarly.py.
R_SITE_GRAPH = [
    {
        "@type": "Person",
        "@id": "#michael-t-wolfinger",
        "name": "Michael T. Wolfinger",
        "givenName": "Michael",
        "familyName": "Wolfinger",
        "jobTitle": "Computational RNA Biologist",
        "email": "michael.wolfinger@rnaforecast.com",
        "url": "https://michaelwolfinger.com/",
        "image": "/static/images/mtw.jpg",
        "affiliation": {"@id": "#organization"},
        "worksFor": {"@id": "#organization"},
        # A typed identifier says *which* identifier scheme this is; a bare
        # URL leaves a consumer to recognise orcid.org by sight.
        "identifier": {"@type": "PropertyValue", "propertyID": "ORCID",
                       "value": "https://orcid.org/0000-0003-0925-5205"},
        "knowsAbout": [
            "Computational RNA biology",
            "RNA secondary structure prediction",
            "RNA folding kinetics",
            "RNA design",
            "Viral RNA biology",
            "Bioinformatics",
        ],
        "sameAs": [
            "https://orcid.org/0000-0003-0925-5205",
            "https://scholar.google.at/citations?user=w0PHGnEAAAAJ&hl=en",
            "https://github.com/mtw",
            "https://www.linkedin.com/in/michaelwolfinger",
            "https://bsky.app/profile/mtwolfinger.bsky.social",
            "https://www.researchgate.net/profile/Michael-Wolfinger",
            "https://www.scopus.com/authid/detail.uri?authorId=6508361997",
            "https://michaelwolfinger.com/",
        ],
    },
    {
        "@type": "Organization",
        "@id": "#organization",
        "name": "RNA Forecast",
        # The registered entity behind the brand. The brand is what the site
        # says everywhere; this is what a machine needs to identify it.
        "legalName": "RNA Forecast e.U.",
        "alternateName": "RNA Forecast, Computational RNA Biology",
        "url": "/",
        # A publisher logo is what Google's Article guidance asks for, and
        # nothing else on the site provided one.
        "logo": {"@type": "ImageObject",
                 "url": "/static/images/RNAF_logo1.png",
                 "width": 1000, "height": 299},
        "email": "michael.wolfinger@rnaforecast.com",
        "description": "Independent research platform for computational RNA "
                       "biology, covering original research, software "
                       "development, collaboration and advanced training.",
        "foundingDate": "2023",
        "founder": {"@id": "#michael-t-wolfinger"},
        "member": {"@id": "#michael-t-wolfinger"},
        "areaServed": "Worldwide",
        # The enquiry channel the site actually offers, which was described
        # in prose and nowhere in the graph.
        "contactPoint": {"@type": "ContactPoint",
                         "contactType": "Research and collaboration enquiries",
                         "email": "michael.wolfinger@rnaforecast.com",
                         "url": "/#contact",
                         "availableLanguage": ["en", "de"]},
        "sameAs": ["https://michaelwolfinger.com/",
                   "https://github.com/mtw"],
        "knowsAbout": [
            "Computational RNA biology",
            "RNA secondary structure prediction",
            "RNA folding kinetics",
            "RNA design",
            "Viral RNA biology",
        ],
        "address": {"@type": "PostalAddress",
                    "postalCode": "3002",
                    "addressLocality": "Purkersdorf",
                    "addressCountry": "AT"},
    },
    {
        # The site itself, which nothing described before: it is what a
        # consumer attaches every page of the site to.
        "@type": "WebSite",
        "@id": "#website",
        "url": "/",
        "name": "RNA Forecast",
        "inLanguage": "en",
        "publisher": {"@id": "#organization"},
    },
    {
        # The home page is about the platform, not the person; ProfilePage
        # belongs on /about/, in R_PAGE_GRAPHS below.
        "@type": "WebPage",
        "@id": "#webpage",
        "url": "/",
        "name": "RNA Forecast, Michael T. Wolfinger",
        "about": {"@id": "#michael-t-wolfinger"},
        "mainEntity": {"@id": "#organization"},
    },
]

# Extra nodes per page, keyed by slug. The Person node is prepended
# automatically, so each page's graph stands on its own.
R_PAGE_GRAPHS = {
    "research": [
        {
            "@type": "CollectionPage",
            "@id": "/research/#webpage",
            "url": "/research/",
            "name": "Research, RNA Forecast",
            "about": {"@id": "#organization"},
            "isPartOf": {"@id": "#website"},
            "inLanguage": "en",
        },
    ],
    "about": [
        {
            "@type": "ProfilePage",
            "@id": "/about/#profilepage",
            "url": "/about/",
            "name": "About Michael T. Wolfinger",
            "mainEntity": {"@id": "#michael-t-wolfinger"},
        },
    ],
}

# Publication dates, keyed by DOI, as deposited with the registration agency.
# The page itself prints only a year, which is all a reader needs; schema.org
# takes the precise date where one exists. A year with no entry here still
# works — the graph simply carries the year, as it did before.
#
# Fetched from Crossref/DataCite, not typed: tests/test_seo.py asserts every
# key is a DOI the page carries and that the years agree, so this cannot
# quietly drift from the bibliography.
R_PUB_DATES = {
    "10.3390/ijms27167228": "2026-08-13",
    "10.1093/nar/gkag473": "2026-05-05",
    "10.1038/s41587-025-02739-0": "2026-06",
    "10.5281/zenodo.15233965": "2025-01-22",
    "10.5281/zenodo.15228717": "2025-03-05",
    "10.1128/jvi.01215-24": "2024-11-19",
    "10.1099/jgv.0.001991": "2024-05-29",
    "10.1038/s41564-023-01587-5": "2024-02-05",
    "10.1139/bcb-2023-0036": "2024-02-01",
    "10.1246/bcsj.20230092": "2023-07-15",
    "10.1093/nar/gkad223": "2023-05-22",
    "10.1007/s12268-023-1907-x": "2023-03",
}

SITEMAP = {
    "format": "xml",
    "hints": False,
    "exclude": ["impressum", "datenschutz", "thanks", "404"]
}

# Search Console token; empty means no meta tag. A DNS TXT record verifies
# the whole domain instead and survives redesigns.
GOOGLE_SITE_VERIFICATION = ''

# GA4 measurement ID; empty means no consent dialog and no script at all,
# which is what a local preview should be. publishconf.py sets it. Google is
# contacted only after the visitor accepts, see base.html.
GOOGLE_ANALYTICS = ''
