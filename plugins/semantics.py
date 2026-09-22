"""Give the rendered pages the semantics reStructuredText cannot express.

Two things the source language genuinely cannot do, both of which a screen
reader needs:

* **Headings inside a container.** RST has no way to put a heading inside a
  `.. container::`, so the publication list — the site's longest page — came
  out as one `<h1>` and 45 KB of `<div>`s. A reader could not list the papers
  or jump between them. The constraint is on RST, not on the HTML that ships,
  so the component divs are promoted to the right heading level here, keeping
  their classes so the stylesheet is untouched.

* **An image's intrinsic size.** The `image` directive's `:width:` option
  emits an inline style, which the stylesheet's layout owns and RST may not
  touch, so a content image shipped with no `width`/`height` at all and the
  browser could not reserve space for it. The file itself knows its size, so
  it is measured here and written onto the tag as plain attributes.

* **A language attribute.** RST can emit a class but never an attribute, so a
  German title inside an English page could not be marked, and an English
  voice reads it as gibberish. A `lang-de` class on the container becomes a
  real `lang="de"`.

Levels are per page, and the page's own `<h1>` is never touched:

    pub-group-h, record-h            -> h2
    pub-title, card-h, collab-h,     -> h3
    subsection-h
"""

import logging
import os
import re
import struct

from pelican import signals

logger = logging.getLogger(__name__)

# class -> heading level. A year group and the closing record sit directly
# under the page title; everything else is subordinate to one of those.
PROMOTE = {
    'pub-group-h': 2,
    'record-h': 2,
    'pub-title': 3,
    'card-h': 3,
    'collab-h': 3,
    'subsection-h': 3,
}

LANGS = {'lang-de': 'de'}

OPEN = re.compile(r'<div class="([^"]*)"\s*>')
# Whether the container holds block content, in which case it cannot itself
# become a heading.
BLOCK_CHILD = re.compile(r'<(?:p|div|ul|ol|dl|table|section)\b')
FIRST_P = re.compile(r'<p>(.*?)</p>', re.S)
# The class the inner heading takes when the container has to stay a div.
HEADING_CLASS = 'component-h'
TAG = re.compile(r'<(/?)div\b[^>]*>')


def closing_tag(content, start):
    """Index of the `</div>` that closes the `<div>` opening at `start`.

    Counting rather than matching non-greedily: these components nest, and a
    `.*?` stops at the first inner `</div>`, silently swallowing whatever it
    contained — which is how the first version of this promoted the year
    groups and quietly skipped every publication title inside them.
    """
    depth = 0
    for match in TAG.finditer(content, start):
        depth += -1 if match.group(1) else 1
        if depth == 0:
            return match.start(), match.end()
    return None


def promote(content):
    """Rewrite the component divs as headings, classes and all."""
    count = 0
    position = 0
    out = []
    while True:
        match = OPEN.search(content, position)
        if not match:
            out.append(content[position:])
            break

        classes = match.group(1).split()
        level = next((PROMOTE[c] for c in classes if c in PROMOTE), None)
        close = closing_tag(content, match.start()) if level else None
        if level is None or close is None:
            out.append(content[position:match.end()])
            position = match.end()
            continue

        lang = next((LANGS[c] for c in classes if c in LANGS), None)
        attr = f' lang="{lang}"' if lang else ''
        inner = content[match.end():close[0]]
        out.append(content[position:match.start()])

        if BLOCK_CHILD.search(inner):
            # A heading may only contain phrasing content, so a container
            # holding a paragraph and a sibling div cannot become one. The
            # year group is like that: the year, then the count beside it.
            # Promote the first paragraph instead and leave the container
            # to go on being the layout box it already is.
            promoted, n = FIRST_P.subn(
                lambda m: f'<h{level} class="{HEADING_CLASS}"{attr}>'
                          f'{m.group(1)}</h{level}>', inner, count=1)
            out.append(f'<div class="{match.group(1)}">{promoted}</div>')
            count += n
        else:
            out.append(
                f'<h{level} class="{match.group(1)}"{attr}>{inner}</h{level}>')
            count += 1
        position = close[1]

    return ''.join(out), count


IMG = re.compile(r'<img\s+([^>]*?)/?>')
SRC = re.compile(r'src="([^"]*)"')
SVG_SIZE = re.compile(r'<svg[^>]*?viewBox="[\d.\s]*?([\d.]+)[\s,]+([\d.]+)"')


def png_size(data):
    if data[:8] == b'\x89PNG\r\n\x1a\n' and data[12:16] == b'IHDR':
        return struct.unpack('>II', data[16:24])
    return None


def jpeg_size(data):
    """Walk the segment chain to the frame header, which carries the size."""
    if data[:2] != b'\xff\xd8':
        return None
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker, length = data[i + 1], struct.unpack('>H', data[i + 2:i + 4])[0]
        # SOF0..SOF15, less the four markers in that range that are not
        # frame headers.
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC, 0xD8):
            height, width = struct.unpack('>HH', data[i + 5:i + 9])
            return width, height
        i += 2 + length
    return None


def svg_size(data):
    match = SVG_SIZE.search(data[:2048].decode('utf-8', 'replace'))
    if match:
        return round(float(match.group(1))), round(float(match.group(2)))
    return None


def measure(path):
    """The image's intrinsic size, or None if it cannot be read."""
    try:
        with open(path, 'rb') as handle:
            data = handle.read(65536)
    except OSError:
        return None
    if path.lower().endswith('.svg'):
        return svg_size(data)
    return png_size(data) or jpeg_size(data)


def size_images(content, content_dir, siteurl):
    """Write each content image's intrinsic size onto its tag."""
    count = 0

    def rewrite(match):
        nonlocal count
        attrs = match.group(1)
        src = SRC.search(attrs)
        if not src or 'width=' in attrs:
            return match.group(0)
        path = src.group(1)
        if siteurl and path.startswith(siteurl):
            path = path[len(siteurl):]
        if '//' in path:                       # someone else's image
            return match.group(0)
        size = measure(os.path.join(content_dir, path.lstrip('/')))
        if not size:
            return match.group(0)
        count += 1
        return f'<img {attrs.rstrip()} width="{size[0]}" height="{size[1]}" />'

    return IMG.sub(rewrite, content), count


def apply(generator):
    for item in list(getattr(generator, 'pages', [])) + \
                list(getattr(generator, 'articles', [])):
        if not item._content:
            continue
        rewritten, count = promote(item._content)
        if count:
            item._content = rewritten
            logger.info('semantics: %s heading(s) on %s', count, item.slug)

        sized, images = size_images(item._content,
                                    generator.settings.get('PATH', 'content'),
                                    generator.settings.get('SITEURL', ''))
        if images:
            item._content = sized
            logger.info('semantics: sized %s image(s) on %s', images,
                        item.slug)


def register():
    signals.page_generator_finalized.connect(apply)
    signals.article_generator_finalized.connect(apply)
