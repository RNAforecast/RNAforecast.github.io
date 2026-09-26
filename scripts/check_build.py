#!/usr/bin/env python3
"""Smoke-test a built site in output/.

Checks that the build produced the pages and assets we expect, that every
reference to the site's own files resolves, and that the pages still request
nothing from a third party — Google Analytics runs behind a consent dialog
that loads it only on acceptance, so an unnoticed CDN reference or a static
Google tag is exactly what that dialog exists to prevent.

Outbound links (<a href> to doi.org, ORCID, GitHub …) are not requests and are
left alone; only subresources — stylesheets, scripts, images, fonts — are held
to the allowed-host list.

Usage: python3 scripts/check_build.py [output_dir]
Exits non-zero and prints one line per problem if anything is wrong.
"""

import html
import json
import os
import re
import struct
import sys
from urllib.parse import unquote, urlsplit

REQUIRED = [
    'index.html',
    'research/index.html',
    'publications/index.html',
    'insights/index.html',
    'about/index.html',
    'impressum/index.html',
    'datenschutz/index.html',
    '404.html',
    'CNAME',
    'robots.txt',
    'llms.txt',
    'sitemap.xml',
    'css/rnaf.css',
    'static/images/og-card.png',
]

# The imprint and the privacy notice: linked from every page for the people
# who need them, but not research content, and carrying a private address.
EXCLUDED_PATHS = ('/impressum/', '/datenschutz/')

# Absent from the sitemap: the two above, plus the pages nobody navigates to.
EXCLUDED_SLUGS = ('impressum', 'datenschutz', 'thanks', '404')

OG_CARD = 'static/images/og-card.png'
OG_CARD_SIZE = (1200, 630)

# Search results truncate around 155-160 characters.
MAX_DESCRIPTION = 150

SITE_HOST = 'rnaforecast.com'

ALLOWED_HOSTS = {SITE_HOST}

# A form action is a data flow, not a subresource: a new host here needs a
# matching disclosure in the privacy notice.
FORM_ACTION_HOSTS = {SITE_HOST, 'formsubmit.co'}

SUBRESOURCE_TAGS = {
    'link', 'script', 'img', 'source', 'iframe', 'video', 'audio', 'embed',
}
LINK_TAGS = {'a', 'area'}

# The consent gate in base.html is the only script the site runs; it is
# recognised by its storage key. Anything else inline is script that crept in.
ALLOWED_INLINE = ("var KEY='rnaf-consent'",)

# The Google tag must only ever be injected by that script after the visitor
# accepts. Written statically, it would load before anyone was asked.
GOOGLE_TAG = 'googletagmanager.com/gtag/js'
CONSENT_DIALOG = 'id="cookie-settings"'

TAG = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)\b([^>]*)>')
ATTR = re.compile(r'\b(href|src|srcset)\s*=\s*["\']([^"\']*)["\']', re.I)
SCRIPT = re.compile(r'<script\b([^>]*)>(.*?)</script>', re.I | re.S)
FORM = re.compile(r'<form\b([^>]*)>', re.I)
ACTION = re.compile(r'\baction\s*=\s*["\']([^"\']*)["\']', re.I)
CSS_URL = re.compile(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)')

NON_FILE = re.compile(r'^(#|mailto:|tel:|data:|javascript:)', re.I)


def html_files(root):
    for dirpath, _, names in os.walk(root):
        for name in names:
            if name.endswith('.html'):
                yield os.path.join(dirpath, name)


def references(attrs):
    """Yield each URL in a tag's attributes, unpacking srcset candidates."""
    for name, value in ATTR.findall(attrs):
        value = html.unescape(value.strip())
        if name.lower() == 'srcset':
            for candidate in value.split(','):
                url = candidate.strip().split()[0] if candidate.strip() else ''
                if url:
                    yield url
        elif value:
            yield value


def local_path(root, page, ref):
    """Path `ref` should resolve to, or None if it points off-site."""
    parts = urlsplit(ref)
    if parts.netloc and parts.netloc != SITE_HOST:
        return None

    if parts.netloc or ref.startswith('/'):
        path = parts.path
    else:
        here = os.path.dirname(os.path.relpath(page, root))
        path = '/' + os.path.normpath(os.path.join(here, parts.path))

    path = unquote(path).lstrip('/')
    if not path or path.endswith('/'):
        path += 'index.html'

    target = os.path.join(root, path)
    return os.path.join(target, 'index.html') if os.path.isdir(target) else target


def check_page(root, page, problems):
    shown = os.path.relpath(page, root)
    with open(page, encoding='utf-8') as f:
        source = f.read()

    if len(source) < 500:
        problems.append(f'{shown}: suspiciously small ({len(source)} bytes)')

    for attrs, body in SCRIPT.findall(source):
        body = body.strip()
        if not body or 'src=' in attrs.lower():
            continue
        if 'application/ld+json' in attrs.lower():
            continue
        if any(marker in body for marker in ALLOWED_INLINE):
            continue
        first = ' '.join(body.split())[:60]
        problems.append(f'{shown}: unexpected inline <script>: {first}')

    for attrs in FORM.findall(source):
        action = ACTION.search(attrs)
        if not action:
            continue
        host = urlsplit(html.unescape(action.group(1))).netloc
        if host and host not in FORM_ACTION_HOSTS:
            problems.append(f'{shown}: form posts to {host}, which is not a '
                            f'declared endpoint')

    seen = set()
    for tag, attrs in TAG.findall(source):
        tag = tag.lower()
        if tag not in SUBRESOURCE_TAGS and tag not in LINK_TAGS:
            continue

        for ref in references(attrs):
            if NON_FILE.match(ref) or (tag, ref) in seen:
                continue
            seen.add((tag, ref))

            host = urlsplit(ref).netloc
            if host and host != SITE_HOST:
                if tag in SUBRESOURCE_TAGS and host not in ALLOWED_HOSTS:
                    problems.append(
                        f'{shown}: third-party request to {host} ({ref})')
                continue  # outbound link, or an allowed external subresource

            target = local_path(root, page, ref)
            if target and not os.path.isfile(target):
                problems.append(f'{shown}: broken reference {ref}')


def png_size(path):
    """(width, height) from a PNG's IHDR, without pulling in an image library."""
    with open(path, 'rb') as f:
        head = f.read(24)
    if len(head) < 24 or head[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    return struct.unpack('>II', head[16:24])


def check_share_card(root, problems):
    path = os.path.join(root, OG_CARD)
    if not os.path.isfile(path):
        return  # already reported as missing

    size = png_size(path)
    if size is None:
        problems.append(f'{OG_CARD}: not a PNG')
    elif size != OG_CARD_SIZE:
        problems.append(f'{OG_CARD}: is {size[0]}x{size[1]}, '
                        f'expected {OG_CARD_SIZE[0]}x{OG_CARD_SIZE[1]}')

    for page in sorted(html_files(root)):
        with open(page, encoding='utf-8') as f:
            source = f.read()
        shown = os.path.relpath(page, root)
        if 'twitter:card' in source and 'og:image' not in source:
            problems.append(f'{shown}: declares twitter:card but has no og:image')
        if '<link rel="canonical"' not in source:
            problems.append(f'{shown}: no canonical link')

        desc = re.search(r'<meta name="description" content="([^"]*)"', source)
        if not desc:
            problems.append(f'{shown}: no meta description')
        else:
            length = len(html.unescape(desc.group(1)))
            if length > MAX_DESCRIPTION:
                problems.append(f'{shown}: meta description is {length} chars, '
                                f'over the {MAX_DESCRIPTION} cap')


def check_consent_gate(root, problems):
    """Google is contacted only after consent, and consent can be changed.

    The gate is a property of the whole page: the tag must not be written as
    a <script src> (the host check catches that too, but this names the real
    problem), the dialog the script shows must exist, and the footer must
    offer a way back into it, or a given consent cannot be withdrawn.
    """
    for page in sorted(html_files(root)):
        shown = os.path.relpath(page, root)
        with open(page, encoding='utf-8') as f:
            source = f.read()

        for attrs, _ in SCRIPT.findall(source):
            if GOOGLE_TAG in attrs:
                problems.append(f'{shown}: the Google tag is a static '
                                f'<script src>, so it loads before consent')

        gated = any(marker in source for marker in ALLOWED_INLINE)
        if not gated:
            if GOOGLE_TAG in source:
                problems.append(f'{shown}: mentions the Google tag without '
                                f'the consent script')
            continue
        if CONSENT_DIALOG not in source:
            problems.append(f'{shown}: consent script without the dialog it '
                            f'shows')
        if 'href="#cookie-settings"' not in source:
            problems.append(f'{shown}: no "Cookie settings" link, so consent '
                            f'cannot be withdrawn')


def check_stylesheet_assets(root, problems):
    """Fonts and images referenced from CSS, which no page links directly.

    A broken url() here costs the site its typography without breaking a
    single page reference, so nothing else would notice.
    """
    for sheet in sorted(os.path.join(dirpath, name)
                        for dirpath, _, names in os.walk(root)
                        for name in names if name.endswith('.css')):
        shown = os.path.relpath(sheet, root)
        with open(sheet, encoding='utf-8') as f:
            css = f.read()

        for ref in CSS_URL.findall(css):
            ref = ref.strip()
            if ref.startswith(('data:', '#')):
                continue

            host = urlsplit(ref).netloc
            if host:
                if host not in ALLOWED_HOSTS:
                    problems.append(f'{shown}: third-party request to {host} ({ref})')
                continue

            if ref.startswith('/'):
                target = os.path.join(root, unquote(ref).lstrip('/'))
            else:
                here = os.path.dirname(sheet)
                target = os.path.normpath(os.path.join(here, unquote(ref)))

            if not os.path.isfile(target):
                problems.append(f'{shown}: url({ref}) does not resolve')


def check_jsonld(root, problems):
    """Every JSON-LD block must parse, and the publication graph must be complete."""
    block = re.compile(
        r'<script type="application/ld\+json">(.*?)</script>', re.I | re.S)

    for page in sorted(html_files(root)):
        shown = os.path.relpath(page, root)
        with open(page, encoding='utf-8') as f:
            source = f.read()

        graphs = []
        for raw in block.findall(source):
            try:
                graphs.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                problems.append(f'{shown}: JSON-LD does not parse ({exc})')

        # The graph is derived from the page's own markup, so a markup change
        # could silently stop producing articles.
        # pub-title is a heading now, and may carry a second class.
        listed = len(re.findall(r'class="[^"]*\bpub-title\b[^"]*"', source))
        if not listed:
            continue

        articles = [node
                    for graph in graphs
                    for node in graph.get('@graph', [])
                    if node.get('@type') == 'ScholarlyArticle']
        if len(articles) != listed:
            problems.append(f'{shown}: {listed} publications on the page but '
                            f'{len(articles)} in the JSON-LD graph')

        page_dois = set(re.findall(r'https://doi\.org/(10\.[^"\'<\s]+)', source))
        graph_dois = {node['identifier']['value']
                      for node in articles
                      if isinstance(node.get('identifier'), dict)}
        for doi in sorted(page_dois - graph_dois):
            problems.append(f'{shown}: DOI {doi} is linked but not in the graph')


def check_excluded_paths(root, problems):
    """Pages kept out of search results and away from LLM readers.

    Keeping EXCLUDED_PATHS out means all three of robots.txt, llms.txt and the
    sitemap have to agree, and each is edited separately.
    """
    robots_path = os.path.join(root, 'robots.txt')
    if os.path.isfile(robots_path):
        with open(robots_path, encoding='utf-8') as f:
            robots = f.read()

        # A named agent group does not inherit the "*" rules.
        records = [r for r in re.split(r'\n\s*\n', robots)
                   if re.search(r'(?im)^User-agent:', r)]
        for record in records:
            agents = re.findall(r'(?im)^User-agent:\s*(\S+)', record)
            for path in EXCLUDED_PATHS:
                if not re.search(rf'(?im)^Disallow:\s*{re.escape(path)}\s*$',
                                 record):
                    problems.append(f'robots.txt: {", ".join(agents)} may '
                                    f'crawl {path}, which is excluded')

    llms_path = os.path.join(root, 'llms.txt')
    if os.path.isfile(llms_path):
        with open(llms_path, encoding='utf-8') as f:
            llms = f.read()
        for label, url in re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', llms):
            for path in EXCLUDED_PATHS:
                if path in url:
                    problems.append(f'llms.txt: links to {path} as "{label}", '
                                    f'which is excluded')


def check_no_accidental_lists(root, problems):
    """Catch reStructuredText turning a line into an enumerated list.

    A publication field starting with something docutils reads as an
    enumerator — "J. General Virology", where J is the 10th letter — becomes
    <ol start="10"><li>…</li></ol>, and the marker shows up on the page while
    the text loses its first token. The fields here are always plain text, so
    any list inside one is this bug.
    """
    block = re.compile(
        r'<(?:div|h[1-6]) class="(pub-badge|pub-title|pub-authors|pub-cite|'
        r'pub-doi|pub-summary|pub-year|tag)[^"]*">(.*?)</(?:div|h[1-6])>', re.S)

    for page in sorted(html_files(root)):
        shown = os.path.relpath(page, root)
        with open(page, encoding='utf-8') as f:
            source = f.read()
        for cls, body in block.findall(source):
            if '<ol' in body or '<ul' in body:
                text = ' '.join(re.sub(r'<[^>]+>', ' ', body).split())[:50]
                problems.append(
                    f'{shown}: .{cls} was parsed as a list, not text — an RST '
                    f'enumerator swallowed the first token: "{text}"')


LINK_TEXT = re.compile(r'<a\b[^>]*>(.*?)</a>', re.S | re.I)
LITERAL_EMAIL = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')


def check_email_text_is_escaped(root, problems):
    """An address shown as link text must escape its @ as &#64;.

    Cloudflare's Email Address Obfuscation runs at the edge, where no build
    check can see it. It scans the served HTML for literal addresses and
    replaces the anchor's *text* with a "[email protected]" placeholder —
    unreadable without JavaScript, which this site does not ship. docutils
    escapes the @ for every address written in RST, so Cloudflare skips those
    and rewrites only the href. A hand-written template is the one place that
    can get it wrong, and it did.
    """
    for page in sorted(html_files(root)):
        shown = os.path.relpath(page, root)
        with open(page, encoding='utf-8') as f:
            source = f.read()
        for text in LINK_TEXT.findall(source):
            found = LITERAL_EMAIL.search(re.sub(r'<[^>]+>', '', text))
            if found:
                problems.append(
                    f'{shown}: link text contains the literal address '
                    f'{found.group(0)}; escape the @ as &#64; or Cloudflare '
                    f'replaces it with a [email protected] placeholder')


def check_fragment_links(root, problems):
    """A link to #something must land on something.

    The research page points at individual publications, and a page anchor is
    the one kind of internal link that breaks silently: the page still loads,
    so nothing looks wrong, and the reader simply arrives at the top of a long
    list instead of at the paper.
    """
    ids = {}
    for page in html_files(root):
        with open(page, encoding='utf-8') as f:
            source = f.read()
        ids[os.path.abspath(page)] = set(re.findall(r'\bid="([^"]+)"', source))

    for page in sorted(html_files(root)):
        shown = os.path.relpath(page, root)
        with open(page, encoding='utf-8') as f:
            source = f.read()

        for tag, attrs in TAG.findall(source):
            if tag.lower() not in LINK_TAGS:
                continue
            for ref in references(attrs):
                if '#' not in ref or ref.startswith(('mailto:', 'tel:')):
                    continue
                path, _, fragment = ref.partition('#')
                if not fragment or urlsplit(ref).netloc not in ('', SITE_HOST):
                    continue

                target = (os.path.abspath(page) if not path
                          else local_path(root, page, path))
                if target is None:
                    continue
                target = os.path.abspath(target)
                if target not in ids:
                    continue  # a missing page is reported by check_page
                if fragment not in ids[target]:
                    problems.append(
                        f'{shown}: link to {ref} lands nowhere — '
                        f'{os.path.relpath(target, root)} has no id '
                        f'"{fragment}"')


def check_venue_badges_alternate(root, problems):
    """Venue badges alternate down each year: filled, outline, filled …

    `.pub-top` fills the badge; without it the badge is the blue outline. The
    alternation is a rhythm, not a statement about the paper, so two adjacent
    badges of the same kind read as meaning something that is not there.
    Nothing enforced it and it had drifted in three of the four year groups.
    """
    group = re.compile(r'<div class="pub-group" id="y(\d{4})">(.*?)'
                       r'(?=<div class="pub-group"|\Z)', re.S)
    # `[^>]*` matters: each entry also carries an id, and without it this
    # regex matches nothing and the check silently passes on everything.
    entry = re.compile(r'<div class="pub([^"]*)"[^>]*>')

    for page in sorted(html_files(root)):
        with open(page, encoding='utf-8') as f:
            source = f.read()
        if 'pub-group' not in source:
            continue
        shown = os.path.relpath(page, root)

        for year, body in group.findall(source):
            flags = [m for m in entry.findall(body)
                     if m in ('', ' pub-top')]
            for i, flag in enumerate(flags):
                filled = 'pub-top' in flag
                if filled == (i % 2 == 0):
                    continue
                problems.append(
                    f'{shown}: venue badges do not alternate in {year}: '
                    f'publication {i + 1} is '
                    f'{"filled" if filled else "outlined"} where it should be '
                    f'{"outlined" if filled else "filled"}')
                break


def check_robots_and_sitemap(root, problems):
    robots_path = os.path.join(root, 'robots.txt')
    if os.path.isfile(robots_path):
        with open(robots_path) as f:
            robots = f.read()
        sitemaps = re.findall(r'(?im)^\s*Sitemap:\s*(\S+)', robots)
        if not sitemaps:
            problems.append('robots.txt: no Sitemap: line')
        for url in sitemaps:
            target = local_path(root, os.path.join(root, 'robots.txt'), url)
            if target and not os.path.isfile(target):
                problems.append(f'robots.txt: Sitemap {url} does not exist')

    sitemap_path = os.path.join(root, 'sitemap.xml')
    if not os.path.isfile(sitemap_path):
        return
    with open(sitemap_path, encoding='utf-8') as f:
        sitemap = f.read()

    for loc in re.findall(r'<loc>([^<]+)</loc>', sitemap):
        target = local_path(root, sitemap_path, loc)
        if target and not os.path.isfile(target):
            problems.append(f'sitemap.xml: {loc} does not exist')

    for slug in EXCLUDED_SLUGS:
        if re.search(rf'<loc>[^<]*/{slug}(/|\.html)?</loc>', sitemap):
            problems.append(f'sitemap.xml: lists /{slug}/, which is excluded')


def check(root):
    problems = []

    for rel in REQUIRED:
        if not os.path.isfile(os.path.join(root, rel)):
            problems.append(f'missing: {rel}')

    cname = os.path.join(root, 'CNAME')
    if os.path.isfile(cname):
        with open(cname) as f:
            host = f.read().strip()
        if host != SITE_HOST:
            problems.append(f'CNAME is {host!r}, expected {SITE_HOST}')

    pages = sorted(html_files(root))
    if not pages:
        problems.append('no HTML pages in output')
    for page in pages:
        check_page(root, page, problems)

    check_share_card(root, problems)
    check_consent_gate(root, problems)
    check_stylesheet_assets(root, problems)
    check_jsonld(root, problems)
    check_no_accidental_lists(root, problems)
    check_venue_badges_alternate(root, problems)
    check_fragment_links(root, problems)
    check_email_text_is_escaped(root, problems)
    check_excluded_paths(root, problems)
    check_robots_and_sitemap(root, problems)

    return problems, len(pages)


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else 'output'
    if not os.path.isdir(root):
        print(f'no such directory: {root}')
        return 1

    problems, pages = check(root)
    for problem in problems:
        print(problem)

    if problems:
        print(f'\n{len(problems)} problem(s) in {pages} page(s)')
        return 1

    print(f'ok: {pages} page(s), all references resolve')
    return 0


if __name__ == '__main__':
    sys.exit(main())
