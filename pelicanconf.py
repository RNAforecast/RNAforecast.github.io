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

# Page metadata whose value is reStructuredText and should reach the template
# as rendered HTML rather than flattened text.
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

# The card every share of the site renders. 1200x630 — the size Open Graph,
# Bluesky, LinkedIn, Slack and Mastodon all expect. Must be a raster image;
# no consumer renders SVG.
M_SOCIAL_IMAGE = 'static/images/og-card.png'

# (label, url, slug) — slug marks the current page in the masthead.
# No 'Home' entry: the wordmark is the link home, and the footer carries an
# explicit one. The wordmark's aria-label in base.html is what makes that
# route discoverable to a screen reader, so keep the two together.
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
                  ('Legal Notice', '/legal/')]

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

# changefreq and priority are omitted: search engines ignore both, and a
# uniform value on every URL carries no information. lastmod comes from the
# source file's mtime, so it only moves when the page actually changes.
# The site's own schema.org graph, emitted on the home page by plugins/
# scholarly.py. Written as data rather than as a raw HTML block in index.rst so
# that the domain is not baked into the content: any "@id" or "url" starting
# with "#" or "/" is prefixed with SITEURL at build time, which means a local
# preview carries no rnaforecast.com at all and production carries it
# everywhere. Keep "#michael-t-wolfinger" in step with AUTHOR_FRAGMENT in the
# plugin — the publication graph refers to the same node.
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
        "@type": "ProfilePage",
        "@id": "#webpage",
        "url": "/",
        "name": "RNA Forecast, Michael T. Wolfinger",
        "about": {"@id": "#michael-t-wolfinger"},
        "mainEntity": {"@id": "#organization"},
    },
]

SITEMAP = {
    "format": "xml",
    "hints": False,
    "exclude": ["legal", "thanks", "404"]
}

# Consent management. Off in development so a local preview sets no cookies at
# all; publishconf.py turns it on. The script URL carries the account and
# configuration ids, so it lives here rather than in the template.
OSANO = False
OSANO_SCRIPT = ('https://cmp.osano.com/AzqaZNTUulxcl8Ml/'
                '1502bf1a-8776-4742-8b0b-35e18285f582/osano.js')

# Google Search Console ownership token — the content= value of the
# google-site-verification meta tag. Empty means the tag is not emitted.
# A DNS TXT record at the registrar verifies the whole domain instead and
# survives redesigns; use this only if you would rather verify by meta tag.
GOOGLE_SITE_VERIFICATION = ''
