#!/usr/bin/env python3
"""Smoke-test a built site in output/.

Checks that the build produced the pages and assets we expect, that every
reference to the site's own files resolves, and that the pages still request
nothing from a third party — the site runs behind a cookie consent banner, so
an unnoticed CDN reference is exactly what that banner exists to gate.

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
    'about/index.html',
    'legal/index.html',
    '404.html',
    'CNAME',
    'robots.txt',
    'llms.txt',
    'sitemap.xml',
    'css/rnaf.css',
    'static/images/og-card.png',
]

OG_CARD = 'static/images/og-card.png'
OG_CARD_SIZE = (1200, 630)

# Search results truncate around 155-160 characters.
MAX_DESCRIPTION = 150

SITE_HOST = 'rnaforecast.com'

ALLOWED_HOSTS = {SITE_HOST, 'www.googletagmanager.com', 'cmp.osano.com'}

# A form action is a data flow, not a subresource: a new host here needs a
# matching disclosure in the legal notice.
FORM_ACTION_HOSTS = {SITE_HOST, 'formsubmit.co'}

SUBRESOURCE_TAGS = {
    'link', 'script', 'img', 'source', 'iframe', 'video', 'audio', 'embed',
}
LINK_TAGS = {'a', 'area'}

# The site ships no JavaScript of its own; only the Consent Mode defaults and
# the Google tag are allowed inline. Anything else is script that crept in.
ALLOWED_INLINE = (
    'window.dataLayer',
    "gtag('js'",
)

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
        if not any(marker in body for marker in ALLOWED_INLINE):
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


def check_consent_order(root, problems):
    """The consent gate only works in one order.

    Consent Mode defaults must run before the Google tag loads, or gtag.js
    stores its cookies before anyone has been asked; and the CMP must come
    before the tag it is supposed to gate. Both are ordering properties, so
    nothing else in the build would notice them being wrong.
    """
    for page in sorted(html_files(root)):
        shown = os.path.relpath(page, root)
        with open(page, encoding='utf-8') as f:
            source = f.read()

        tag = source.find('googletagmanager.com/gtag/js')
        if tag == -1:
            continue

        default = source.find("gtag('consent', 'default'")
        if default == -1:
            problems.append(f'{shown}: Google tag without Consent Mode defaults')
        elif default > tag:
            problems.append(f'{shown}: Consent Mode defaults come after the '
                            f'Google tag, so cookies are set before consent')

        if "analytics_storage: 'denied'" not in source:
            problems.append(f'{shown}: analytics_storage is not denied by default')

        cmp_at = source.find('osano.js')
        if cmp_at != -1 and cmp_at > tag:
            problems.append(f'{shown}: the consent platform loads after the '
                            f'Google tag it is meant to gate')


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
        listed = source.count('class="pub-title"')
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

    The legal notice is the imprint and privacy statement: linked from every
    page for the people who need it, but not research content. Keeping it out
    means all three of robots.txt, llms.txt and the sitemap have to agree, and
    each is edited separately.
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
            if not re.search(r'(?im)^Disallow:\s*/legal/\s*$', record):
                problems.append(f'robots.txt: {", ".join(agents)} may crawl '
                                f'/legal/, which is excluded')

    llms_path = os.path.join(root, 'llms.txt')
    if os.path.isfile(llms_path):
        with open(llms_path, encoding='utf-8') as f:
            llms = f.read()
        for label, url in re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', llms):
            if '/legal/' in url:
                problems.append(f'llms.txt: links to the legal notice as '
                                f'"{label}", which is excluded')


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

    for slug in ('legal', 'thanks', '404'):
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
    check_consent_order(root, problems)
    check_stylesheet_assets(root, problems)
    check_jsonld(root, problems)
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
