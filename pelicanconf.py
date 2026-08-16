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
ARTICLE_PATHS = ['articles']  # no blog; keeps the article generator quiet

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
                   ('Software', '/#software', ''),
                   ('Collaborations', '/#collaborations', ''),
                   ('Teaching & Training', '/#training', ''),
                   ('About', '/about/', 'about'),
                   ('Contact', '/#contact', '')]

R_FOOTER_TAGLINE = ('Independent research platform · Computational RNA biology '
                    '· Vienna, Austria')

R_FOOTER_LINKS = [('Home', '/'),
                  ('Research', '/research/'),
                  ('Publications', '/publications/'),
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
                    "addressLocality": "Vienna",
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
