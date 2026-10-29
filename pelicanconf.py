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
                   ('Training', '/training/', 'training'),
                   ('About', '/about/', 'about'),
                   ('Contact', '/#contact', '')]

R_FOOTER_TAGLINE = ('Independent research platform · Computational RNA biology '
                    '· Purkersdorf / Vienna, Austria')

R_FOOTER_LINKS = [('Home', '/'),
                  ('Research', '/research/'),
                  ('Publications', '/publications/'),
                  ('Insights', '/insights/'),
                  ('Training', '/training/'),
                  ('About', '/about/'),
                  ('Impressum', '/impressum/'),
                  ('Datenschutz', '/datenschutz/')]

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
    # Icons beyond the .ico: an SVG for modern tabs, the Apple touch icon at
    # the root where iOS looks first, and the manifest that names the PNGs.
    'extra/favicon.svg': {'path': 'favicon.svg'},
    'extra/apple-touch-icon.png': {'path': 'apple-touch-icon.png'},
    'extra/site.webmanifest': {'path': 'site.webmanifest'},
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
        "honorificPrefix": "Mag. Dr.",
        "jobTitle": "Computational RNA Biologist",
        "hasOccupation": {"@type": "Occupation",
                          "name": "Computational RNA biologist",
                          "occupationLocation": {"@type": "City",
                                                 "name": "Vienna"}},
        "alumniOf": {"@type": "CollegeOrUniversity",
                     "name": "University of Vienna",
                     "sameAs": "https://www.univie.ac.at/"},
        "knowsLanguage": ["en", "de"],
        "address": {"@type": "PostalAddress",
                    "addressLocality": "Purkersdorf",
                    "addressCountry": "AT"},
        "email": "hello@rnaforecast.com",
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
        # Registry identifiers, both public in the Impressum: what lets a
        # consumer merge this node with the commercial register entry.
        "vatID": "ATU78022612",
        "identifier": {"@type": "PropertyValue",
                       "propertyID": "Firmenbuchnummer",
                       "value": "FN 597678p"},
        "url": "/",
        # A publisher logo is what Google's Article guidance asks for, and
        # nothing else on the site provided one.
        "logo": {"@type": "ImageObject",
                 "url": "/static/images/RNAF_logo1.png",
                 "width": 1000, "height": 299},
        "email": "hello@rnaforecast.com",
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
                         "email": "hello@rnaforecast.com",
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
        "name": "RNA Forecast",
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
    "training": [
        {
            "@type": "WebPage",
            "@id": "/training/#webpage",
            "url": "/training/",
            "name": "Training, RNA Forecast",
            "about": {"@id": "#organization"},
            "mainEntity": {"@type": "ItemList",
                           "itemListElement": [
                               {"@type": "ListItem", "position": 1,
                                "item": {"@id": "/training/#viennarna"}},
                               {"@type": "ListItem", "position": 2,
                                "item": {"@id": "/training/#local-ai-tools"}}]},
        },
        # Courses in preparation: no Offer and no CourseInstance on purpose,
        # since nothing is scheduled or bookable yet. Add both when it is.
        {
            "@type": "Course",
            "@id": "/training/#viennarna",
            "url": "/training/#viennarna",
            "name": "ViennaRNA and computational RNA design",
            "description": "Hands-on training for research groups: RNA "
                           "secondary structure and the Boltzmann ensemble, "
                           "probing data as soft constraints, folding "
                           "kinetics, accessibility, and design review before "
                           "synthesis. Half day to full day, remote or on site.",
            "provider": {"@id": "#organization"},
            "instructor": {"@id": "#michael-t-wolfinger"},
            "courseMode": ["online", "onsite"],
            "inLanguage": "en",
            "teaches": ["RNA secondary structure prediction", "ViennaRNA",
                        "RNA folding kinetics", "RNA design"],
            "educationalLevel": "Intermediate",
            "audience": {"@type": "EducationalAudience",
                         "educationalRole": "researcher",
                         "audienceType": "Experimental RNA labs, biotech "
                                         "teams, doctoral programmes"},
        },
        {
            "@type": "Course",
            "@id": "/training/#local-ai-tools",
            "url": "/training/#local-ai-tools",
            "name": "Local AI coding tools for research groups",
            "description": "A scientist's half-day workshop on running coding "
                           "agents against models on the group's own "
                           "hardware: model choice, setup on macOS and Linux, "
                           "a research workflow, privacy and cost.",
            "provider": {"@id": "#organization"},
            "instructor": {"@id": "#michael-t-wolfinger"},
            "courseMode": ["online", "onsite"],
            "inLanguage": "en",
            "teaches": ["Local large language models", "Coding agents",
                        "Reproducible research workflows"],
            "educationalLevel": "Beginner",
            "audience": {"@type": "EducationalAudience",
                         "educationalRole": "researcher",
                         "audienceType": "Research groups whose data must "
                                         "stay on their own machines"},
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

# What the registration agency knows about each journal paper and the page
# does not print: the co-authors' given names (the full listing writes
# surnames only), the journal's ISSN and full title, volume, issue and pages.
# plugins/scholarly.py merges it into each ScholarlyArticle, so a consumer
# can match the authors and the venue instead of guessing from a surname and
# an abbreviation. Fetched from Crossref, not typed, and like R_PUB_DATES
# pinned to the page by tests/test_seo.py: every key is a DOI on the page and
# the surnames agree in order. The owner is referenced by @id, never listed
# here. The two Zenodo workshop papers have no Crossref record and no entry.
R_PUB_META = {
    "10.3390/ijms27167228": {
        "journal": "International Journal of Molecular Sciences",
        "issn": ["1422-0067"],
        "volume": "27",
        "issue": "16",
        "pages": "7228",
        "authors": [
            ("Aman", "Aamir"),
            ("Sidl", "Leonhard"),
            ("Darai", "Nitchakan"),
            ("Wolschann", "Peter"),
            ("Rungrotmongkol", "Thanyada"),
        ],
    },
    "10.1093/nar/gkag473": {
        "journal": "Nucleic Acids Research",
        "issn": ["0305-1048", "1362-4962"],
        "volume": "54",
        "issue": "9",
        "authors": [
            ("Walter", "Jule"),
            ("Sidl", "Leonhard"),
            ("Gutenbrunner", "Katrin"),
            ("Skibinski", "Denis"),
            ("Kolberg", "Tim"),
            ("Hofacker", "Ivo L"),
            ("Yao", "Hua-Ting"),
            ("Mörl", "Mario"),
        ],
    },
    "10.1038/s41587-025-02739-0": {
        "journal": "Nature Biotechnology",
        "issn": ["1087-0156", "1546-1696"],
        "volume": "44",
        "issue": "6",
        "pages": "989-1001",
        "authors": [
            ("Borovská", "Ivana"),
            ("Zhang", "Chundan"),
            ("Dülk", "Sarah-Luisa J."),
            ("Morandi", "Edoardo"),
            ("Cardoso", "Marta F. S."),
            ("Bourkia", "Billal M."),
            ("van den Homberg", "Daphne A. L."),
            ("Velema", "Willem A."),
            ("Incarnato", "Danny"),
        ],
    },
    "10.2306/scienceasia1513-1874.2025.s013": {
        "journal": "ScienceAsia",
        "issn": ["1513-1874"],
        "volume": "51S",
        "issue": "1",
        "pages": "1-10",
        "authors": [
            ("Darai", "Nitchakan"),
            ("Sidl", "Leonhard"),
            ("Rungrotmongkol", "Thanyada"),
            ("Wolschann", "Peter"),
        ],
    },
    "10.1128/jvi.01215-24": {
        "journal": "Journal of Virology",
        "issn": ["0022-538X", "1098-5514"],
        "volume": "98",
        "issue": "11",
        "authors": [
            ("Besson", "Benoit"),
            ("Overheul", "Gijs J."),
            ("Junglen", "Sandra"),
            ("van Rij", "Ronald P."),
        ],
    },
    "10.1099/jgv.0.001991": {
        "journal": "Journal of General Virology",
        "issn": ["0022-1317", "1465-2099"],
        "volume": "105",
        "issue": "5",
        "authors": [
            ("Wang", "Lan-Lan"),
            ("Cheng", "Qia"),
            ("Newton", "Natalee D."),
            ("Morgan", "Mahali S."),
            ("Slonchak", "Andrii"),
            ("Khromykh", "Alexander A."),
            ("Cheng", "Tian-Yin"),
            ("Parry", "Rhys H."),
        ],
    },
    "10.1038/s41564-023-01587-5": {
        "journal": "Nature Microbiology",
        "issn": ["2058-5276"],
        "volume": "9",
        "issue": "2",
        "pages": "550-560",
        "authors": [
            ("McBroome", "Jakob"),
            ("de Bernardi Schneider", "Adriano"),
            ("Roemer", "Cornelius"),
            ("Hinrichs", "Angie S."),
            ("O'Toole", "Aine Niamh"),
            ("Ruis", "Christopher"),
            ("Turakhia", "Yatish"),
            ("Rambaut", "Andrew"),
            ("Corbett-Detig", "Russell"),
        ],
    },
    "10.1139/bcb-2023-0036": {
        "journal": "Biochemistry and Cell Biology",
        "issn": ["0829-8211", "1208-6002"],
        "volume": "102",
        "issue": "1",
        "pages": "96-105",
        "authors": [
            ("Gemmill", "Dannielle L."),
            ("Nelson", "Corey R."),
            ("Badmalia", "Maulik D."),
            ("Pereira", "Higor S."),
            ("Kerr", "Liam"),
            ("Patel", "Trushar R."),
        ],
    },
    "10.1246/bcsj.20230092": {
        "journal": "Bulletin of the Chemical Society of Japan",
        "issn": ["0009-2673", "1348-0634"],
        "volume": "96",
        "issue": "7",
        "pages": "677-685",
        "authors": [
            ("Darai", "Nitchakan"),
            ("Hengphasatporn", "Kowit"),
            ("Wolschann", "Peter"),
            ("Shigeta", "Yasuteru"),
            ("Rungrotmongkol", "Thanyada"),
            ("Harada", "Ryuhei"),
        ],
    },
    "10.1093/nar/gkad223": {
        "journal": "Nucleic Acids Research",
        "issn": ["0305-1048", "1362-4962"],
        "volume": "51",
        "issue": "9",
        "pages": "4588-4601",
        "authors": [
            ("Mrozowich", "Tyler"),
            ("Park", "Sean M"),
            ("Waldl", "Maria"),
            ("Henrickson", "Amy"),
            ("Tersteeg", "Scott"),
            ("Nelson", "Corey R"),
            ("De Klerk", "Anneke"),
            ("Demeler", "Borries"),
            ("Hofacker", "Ivo L"),
            ("Patel", "Trushar R"),
        ],
    },
    "10.1007/s12268-023-1907-x": {
        "journal": "BIOspektrum",
        "issn": ["0947-0867", "1868-6249"],
        "volume": "29",
        "issue": "2",
        "pages": "156-158",
        "authors": [
            ("Ochsenreiter", "Roman"),
        ],
    },
}

SITEMAP = {
    "format": "xml",
    "hints": False,
    "exclude": ["impressum", "datenschutz", "thanks", "waitlist", "404"]
}

# The form handler (repo mtw/form-handler, a Cloudflare Worker): every form
# posts to <FORM_HANDLER>/<form-id>. The content writes the production URL;
# the build rewrites the base to this value (plugins/semantics.py), so a
# preview Worker can be tried by changing one line. scripts/check_build.py
# fails a form that posts anywhere else or to an unknown form id.
FORM_HANDLER = 'https://forms.rnaforecast.com'

# Search Console token; empty means no meta tag. A DNS TXT record verifies
# the whole domain instead and survives redesigns.
GOOGLE_SITE_VERIFICATION = ''

# GA4 measurement ID; empty means no consent dialog and no script at all,
# which is what a local preview should be. publishconf.py sets it. Google is
# contacted only after the visitor accepts, see base.html.
GOOGLE_ANALYTICS = ''
