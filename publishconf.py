
import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = "https://rnaforecast.com"
RELATIVE_URLS = False


DELETE_OUTPUT_DIRECTORY = True


# The rnaforecast.com property. Consent-gated in base.html: the built page
# requests nothing from Google until the visitor accepts.
GOOGLE_ANALYTICS = 'G-XDJC7M3EQS'

# Draft pages (``:status: draft``) are rendered under drafts/pages/ by the
# development build for proofreading and are not written at all in production.
DRAFT_PAGE_URL = ''
DRAFT_PAGE_SAVE_AS = ''
