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

M_CSS_FILES = ['/css/m-rnaf.css',
               'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css']

M_THEME_COLOR = '#cb4b16'

PLUGIN_PATHS = ['plugins']
PLUGINS = ['m.htmlsanity',
           'm.components',
           'm.link',
           'sitemap',
           'm.images']

#M_BLOG_NAME = 'RNA Forecast Blog'
#M_BLOG_URL = 'blog/'

M_FAVICON = ('favicon.ico', 'image/x-ico')

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

M_SITE_LOGO = 'static/images/RNAF_black_xx.png'
M_SITE_LOGO_TEXT = ''


M_LINKS_NAVBAR1 = [#('Services', 'services/', 'services', []),
                   #('Training', 'training/', 'training', []),
                   #('Research', 'research/', 'research', []),
                   #('About', 'about/', 'about', []),
                   ('Contact', 'contact/', 'contact', [])]


# Social widget
SOCIAL = (
    ("You can add links in your config file", "#"),
    ("Another social link", "#"),
)

M_LINKS_FOOTER1 = [('RNA Forecast', '/'),
                    ('Contact', 'contact/'),
                    ('Legal', 'legal/')]

#M_LINKS_FOOTER2 = [('Social Media', ''),
#                   ('LinkedIn', 'https://www.linkedin.com/company/rnaforecast')]

M_LINKS_FOOTER4 = []

R_LINKEDIN_URL = 'https://www.linkedin.com/company/rnaforecast'

DEFAULT_PAGINATION = 10

M_FINE_PRINT =  """
© 2025 RNA Forecast e.U. | All rights reserved
"""

STATIC_PATHS = ['static', 'extra', 'css']
EXTRA_PATH_METADATA = {
    'extra/robots.txt': {'path': 'robots.txt'},
    'extra/favicon.ico': {'path': 'favicon.ico'},
    'extra/CNAME': {'path': 'CNAME'},
}

PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'
#ARTICLE_URL = 'blog/{date:%Y}/{slug}/'
#ARTICLE_SAVE_AS = 'blog/{date:%Y}/{slug}/index.html'
#INDEX_SAVE_AS = 'blog/index.html'


# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

SITEMAP = {
    "format": "xml",
    "priorities": {
        "articles": 0.5,
        "indexes": 0.5,
        "pages": 0.5
    },
    "changefreqs": {
        "articles": "always",
        "indexes": "always",
        "pages": "always"
    },
    "exclude": ["blog/archive/", "blog/author/", "authors", "index", "legal"]
}
