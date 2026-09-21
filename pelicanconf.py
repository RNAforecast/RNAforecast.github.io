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

M_CSS_FILES = ['/css/rnaf.css']

FORMATTED_FIELDS = ['summary', 'hero_links', 'hero_actions', 'hero_body']

M_THEME_COLOR = '#5980a6'

PLUGIN_PATHS = ['plugins']
PLUGINS = ['m.htmlsanity',   # the HTML5 RST writer the whole stylesheet targets
           'scholarly',      # schema.org data derived from the publications page
           'sitemap']

M_FAVICON = ('favicon.ico', 'image/x-ico')

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

M_SITE_LOGO = 'static/images/rnaforecast-logo.svg'
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
EXTRA_PATH_METADATA = {
    'extra/robots.txt': {'path': 'robots.txt'},
    'extra/favicon.ico': {'path': 'favicon.ico'},
    'extra/CNAME': {'path': 'CNAME'},
    'extra/llms.txt': {'path': 'llms.txt'},
}

PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

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
        "email": "mailto:michael.wolfinger@rnaforecast.com",
        "url": "https://michaelwolfinger.com/",
        "image": "/static/images/mtw.jpg",
        "affiliation": {"@id": "#organization"},
        "identifier": "https://orcid.org/0000-0003-0925-5205",
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
        "alternateName": "RNA Forecast, Computational RNA Biology",
        "url": "/",
        "email": "mailto:michael.wolfinger@rnaforecast.com",
        "description": "Independent research platform for computational RNA "
                       "biology, covering original research, software "
                       "development, collaboration and advanced training.",
        "foundingDate": "2023",
        "founder": {"@id": "#michael-t-wolfinger"},
        "member": {"@id": "#michael-t-wolfinger"},
        "areaServed": "Worldwide",
        "address": {"@type": "PostalAddress",
                    "postalCode": "3002",
                    "addressLocality": "Purkersdorf",
                    "addressCountry": "AT"},
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

SITEMAP = {
    "format": "xml",
    "hints": False,
    "exclude": ["impressum", "datenschutz", "thanks", "404"]
}

# Search Console token; empty means no meta tag. A DNS TXT record verifies
# the whole domain instead and survives redesigns.
GOOGLE_SITE_VERIFICATION = ''
