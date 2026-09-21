"""Emit schema.org data: ScholarlyArticle for publications, Article for Insights.

The publication list is written as reStructuredText containers, and RST cannot
produce a <script> block or a data- attribute. Rather than keep a second copy
of the bibliography in JSON — which would drift from the prose the moment a
paper is added — this plugin reads the page Pelican has already rendered and
derives the structured data from it.

It looks for the markup the page actually uses:

    .pub-group#yYYYY  >  .pub  >  .pub-badge   journal name
                                  .pub-title   article title
                                  .pub-authors author list, comma separated
                                  .pub-cite    citation line, year in (…)
                                  .pub-summary plain-language abstract
                                  .pub-doi     "doi:10.…"

The result lands on the page object as `page.jsonld`, which page.html emits.
scripts/check_build.py asserts that every publication on the page reached the
graph, so a markup change that silently breaks extraction fails the build.

Insights are different: an article's metadata already says everything the
Article node needs, so nothing is scraped. Each Insight gets an Article node
and /insights/ a CollectionPage listing them, and both carry the Person and
Organization nodes they reference so the graph stands on its own.
"""

import json
import logging
import re
from html.parser import HTMLParser

from pelican import signals

logger = logging.getLogger(__name__)

# AUTHOR_FRAGMENT must match the Person @id in R_SITE_GRAPH, or the site graph
# and the publication graph describe two different people.
AUTHOR_NAME = 'Michael T. Wolfinger'
AUTHOR_FRAGMENT = '#michael-t-wolfinger'
AUTHOR_ORCID = 'https://orcid.org/0000-0003-0925-5205'
# The two pages cite him differently; both must resolve to the same node.
AUTHOR_ALIASES = {'Michael T. Wolfinger', 'Wolfinger MT', 'Wolfinger M.T.'}

DOI_RE = re.compile(r'\b10\.\d{4,9}/\S+')
YEAR_RE = re.compile(r'\((\d{4})\)')


class Node:
    """The little of a DOM that this plugin needs."""

    def __init__(self, tag, attrs=None):
        self.tag = tag
        attrs = dict(attrs or ())
        self.classes = set(attrs.get('class', '').split())
        self.id = attrs.get('id', '')
        self.href = attrs.get('href', '')
        self.children = []
        # Document order matters: an emphasised name in the middle of an
        # author list must not end up at the end of it.
        self.parts = []

    def add_text(self, text):
        self.parts.append(text)

    def add_child(self, node):
        self.parts.append(node)
        self.children.append(node)

    def hrefs(self):
        for node in self.walk():
            if node.href:
                yield node.href

    @property
    def text(self):
        """Collapsed text of this node and everything under it, in order."""
        flat = ''.join(part if isinstance(part, str) else part.text
                       for part in self.parts)
        return ' '.join(flat.split())

    def find(self, cls):
        """First descendant carrying `cls`, or None."""
        for node in self.walk():
            if cls in node.classes:
                return node
        return None

    def find_all(self, cls):
        return [node for node in self.walk() if cls in node.classes]

    def walk(self):
        for child in self.children:
            yield child
            yield from child.walk()


class Tree(HTMLParser):
    VOID = {'br', 'img', 'hr', 'meta', 'link', 'input', 'source'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('root')
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        node = Node(tag, attrs)
        self.stack[-1].add_child(node)
        self.stack.append(node)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].add_text(data)


def text_of(node, *classes):
    """Text of the first of `classes` present, so both page layouts work."""
    for cls in classes:
        found = node.find(cls)
        if found and found.text:
            return found.text
    return ''


def doi_of(pub):
    """DOI from the .pub-doi line, or failing that from a doi.org link."""
    match = DOI_RE.search(text_of(pub, 'pub-doi'))
    if not match:
        for href in pub.hrefs():
            match = re.search(r'doi\.org/(10\.\d{4,9}/\S+)', href)
            if match:
                return match.group(1).rstrip('.,;')
        return ''
    return match.group(0).rstrip('.,;')


def author_node(author_id):
    return {
        '@type': 'Person',
        '@id': author_id,
        'name': AUTHOR_NAME,
        'identifier': AUTHOR_ORCID,
        'sameAs': AUTHOR_ORCID,
    }


def make_author(name, author_id):
    name = name.strip(' ,')
    if not name:
        return None
    if name in AUTHOR_ALIASES:
        return {'@id': author_id}
    return {'@type': 'Person', 'name': name}


def article_from(pub, fallback_year, author_id):
    """Build one ScholarlyArticle, or None if the block has no title."""
    title = text_of(pub, 'pub-title')
    if not title:
        return None

    doi = doi_of(pub)
    cite = text_of(pub, 'pub-cite')
    year_match = YEAR_RE.search(cite)
    if year_match:
        year = year_match.group(1)
    else:
        year = text_of(pub, 'pub-year').strip() or fallback_year
        year = year if re.fullmatch(r'\d{4}', year or '') else fallback_year

    article = {'@type': 'ScholarlyArticle', 'name': title, 'headline': title}

    if doi:
        article['@id'] = f'https://doi.org/{doi}'
        article['url'] = f'https://doi.org/{doi}'
        article['sameAs'] = f'https://doi.org/{doi}'
        article['identifier'] = {
            '@type': 'PropertyValue',
            'propertyID': 'DOI',
            'value': doi,
        }

    authors = [make_author(part, author_id)
               for part in text_of(pub, 'pub-authors').split(',')]
    authors = [author for author in authors if author]
    if authors:
        article['author'] = authors

    if year:
        article['datePublished'] = year

    journal = text_of(pub, 'pub-badge', 'tag')
    if journal:
        article['isPartOf'] = {'@type': 'Periodical', 'name': journal}

    summary = text_of(pub, 'pub-summary')
    if summary:
        # abstract is the scholarly property; description is what generic
        # consumers read.
        article['abstract'] = summary
        article['description'] = summary

    if cite:
        article['citation'] = cite

    return article


def absolutise(value, site_url, key=None):
    """Expand site-relative "@id"/"url" values against SITEURL.

    "#node" and "/path" become "<siteurl>/#node" and "<siteurl>/path". With an
    empty SITEURL — the development build — they stay relative, so a local
    preview contains no production domain anywhere.
    """
    if isinstance(value, dict):
        return {k: absolutise(v, site_url, k) for k, v in value.items()}
    if isinstance(value, list):
        return [absolutise(v, site_url, key) for v in value]
    if (key in ('@id', 'url', 'image')
            and isinstance(value, str) and value[:1] in ('#', '/')):
        return f'{site_url}{"/" if value[0] == "#" else ""}{value}'
    return value


def referenced_ids(value, found=None):
    """Every bare {"@id": ...} reference anywhere in a graph."""
    found = set() if found is None else found
    if isinstance(value, dict):
        if set(value) == {'@id'}:
            found.add(value['@id'])
        for item in value.values():
            referenced_ids(item, found)
    elif isinstance(value, list):
        for item in value:
            referenced_ids(item, found)
    return found


def resolve_references(nodes, available):
    """Append any referenced node that is defined elsewhere in the site graph.

    A page whose Person carries `affiliation: {"@id": "…#organization"}` should
    ship the Organization too, or the reference dangles for anything reading
    that page on its own.
    """
    present = {n.get('@id') for n in nodes if n.get('@id')}
    by_id = {n.get('@id'): n for n in available if n.get('@id')}
    for ref in sorted(referenced_ids(nodes) - present):
        if ref in by_id:
            nodes.append(by_id[ref])
            present.add(ref)
    return nodes


def build_graph(content, page_url, page_name, site_url):
    tree = Tree()
    tree.feed(content)
    author_id = f'{site_url}/{AUTHOR_FRAGMENT}' if site_url else AUTHOR_FRAGMENT

    articles = []
    for group in tree.root.find_all('pub-group'):
        year = group.id[1:] if re.fullmatch(r'y\d{4}', group.id) else ''
        for pub in group.find_all('pub'):
            article = article_from(pub, year, author_id)
            if article:
                articles.append(article)

    grouped = {id(pub) for group in tree.root.find_all('pub-group')
               for pub in group.find_all('pub')}
    for pub in tree.root.find_all('pub'):
        if id(pub) not in grouped:
            article = article_from(pub, '', author_id)
            if article:
                articles.append(article)

    if not articles:
        return None

    graph = [author_node(author_id)]

    # Only the full listing is a CollectionPage; a page that merely features
    # papers is not the bibliography.
    if tree.root.find('pub-group'):
        graph.append({
            '@type': 'CollectionPage',
            '@id': f'{page_url}#webpage',
            'name': page_name,
            'url': page_url,
            'about': {'@id': author_id},
            'hasPart': [{'@id': a['@id']} for a in articles if '@id' in a],
        })

    return {'@context': 'https://schema.org', '@graph': graph + articles}


def to_script_body(graph):
    """JSON safe to drop inside a <script> element.

    Escaping the angle brackets means a "</script>" appearing in a title or
    abstract cannot close the element early.
    """
    body = json.dumps(graph, indent=2, ensure_ascii=False)
    return (body.replace('&', '\\u0026')
                .replace('<', '\\u003c')
                .replace('>', '\\u003e'))


def site_nodes(settings, siteurl, *ids):
    """The named nodes of R_SITE_GRAPH, absolutised, in the order given.

    An Insight's graph references the Person as its author and the
    Organization as its publisher, so both have to travel with it: a page
    that points at an @id it does not define cannot be read on its own.
    """
    site_graph = settings.get('R_SITE_GRAPH') or []
    by_id = {node.get('@id'): node for node in site_graph}
    return [absolutise(by_id[i], siteurl) for i in ids if i in by_id]


def article_node(article, settings, siteurl):
    """One schema.org Article, built from the article's own metadata."""
    url = f'{siteurl}/{article.url}' if siteurl else f'/{article.url}'
    author_id = absolutise(AUTHOR_FRAGMENT, siteurl, '@id')
    org_id = absolutise('#organization', siteurl, '@id')

    image = getattr(article, 'hero_image', None) or settings.get('M_SOCIAL_IMAGE')
    description = getattr(article, 'description', '') or ''
    if not description:
        description = re.sub(r'<[^>]+>', ' ', getattr(article, 'summary', '') or '')
        description = ' '.join(description.split())

    node = {
        '@type': 'Article',
        '@id': f'{url}#article',
        'headline': article.title,
        'name': article.title,
        'url': url,
        'mainEntityOfPage': {'@type': 'WebPage', '@id': url},
        'datePublished': article.date.date().isoformat(),
        'dateModified': (getattr(article, 'modified', None)
                         or article.date).date().isoformat(),
        'inLanguage': getattr(article, 'lang', None) or 'en',
        'author': {'@id': author_id},
        'publisher': {'@id': org_id},
        'isAccessibleForFree': True,
    }
    if description:
        node['description'] = description
    # The bibliographic abstract, the same text the deposit record carries.
    # `abstract` is the scholarly property; `description` is what generic
    # consumers read — the publications page makes the same distinction.
    # `bib_abstract`, because docutils reserves `abstract` for a body topic.
    abstract = getattr(article, 'bib_abstract', None)
    if abstract:
        node['abstract'] = abstract
    if image:
        node['image'] = absolutise(f'/{image.lstrip("/")}', siteurl, 'image')
    keywords = [tag.name for tag in getattr(article, 'tags', None) or []]
    if keywords:
        node['keywords'] = keywords

    # From metadata.yaml, by way of the generated article: an Insight that has
    # been deposited says so here too, so the page and the archival record
    # describe one publication rather than two.
    version = getattr(article, 'version', None)
    if version:
        node['version'] = version
    series = getattr(article, 'series', None)
    number = getattr(article, 'number', None)
    if series:
        part = {'@type': 'PublicationIssue', 'name': series}
        if number:
            part['issueNumber'] = number
        node['isPartOf'] = part
    doi = getattr(article, 'doi', None)
    if doi:
        node['identifier'] = {'@type': 'PropertyValue',
                              'propertyID': 'DOI', 'value': doi}
        node['sameAs'] = f'https://doi.org/{doi}'
    license_ = getattr(article, 'license', None)
    if license_:
        node['license'] = license_
    return node


def attach_articles(article_generator):
    """Article JSON-LD for every published Insight."""
    settings = article_generator.settings
    siteurl = settings.get('SITEURL', '')

    for article in article_generator.articles:
        nodes = site_nodes(settings, siteurl, AUTHOR_FRAGMENT, '#organization')
        nodes.append(article_node(article, settings, siteurl))
        article.jsonld = to_script_body(
            {'@context': 'https://schema.org', '@graph': nodes})
        logger.info('scholarly: Article node on %s', article.slug)


def insights_nodes(page, articles, settings, siteurl):
    """The library page: a CollectionPage whose list names each Insight.

    A plain ItemList of names and URLs, not @id references: the landing page
    does not carry the article nodes themselves, and a reference to a node it
    does not define would dangle.
    """
    page_url = f'{siteurl}/{page.url}' if siteurl else f'/{page.url}'
    items = [
        {'@type': 'ListItem', 'position': i, 'name': article.title,
         'url': f'{siteurl}/{article.url}' if siteurl else f'/{article.url}'}
        for i, article in enumerate(
            sorted(articles, key=lambda a: a.date, reverse=True), start=1)
    ]
    collection = {
        '@type': 'CollectionPage',
        '@id': f'{page_url}#webpage',
        'url': page_url,
        'name': page.title,
        'about': {'@id': absolutise('#organization', siteurl, '@id')},
    }
    if items:
        collection['mainEntity'] = {
            '@type': 'ItemList', 'numberOfItems': len(items),
            'itemListOrder': 'https://schema.org/ItemListOrderDescending',
            'itemListElement': items,
        }
    return [collection]


def attach(page_generator):
    settings = page_generator.settings
    siteurl = settings.get('SITEURL', '')
    site_graph = settings.get('R_SITE_GRAPH') or []
    page_graphs = settings.get('R_PAGE_GRAPHS') or {}
    author_id = absolutise(AUTHOR_FRAGMENT, siteurl, '@id')
    person = next((n for n in site_graph
                   if n.get('@id') == AUTHOR_FRAGMENT), None)

    for page in page_generator.pages:
        is_home = getattr(page, 'save_as', '') == 'index.html'
        has_pubs = page.content and 'pub-title' in page.content
        is_insights = page.slug == 'insights'
        extra = page_graphs.get(page.slug)
        if not is_home and not has_pubs and not extra and not is_insights:
            continue

        page_url = f'{siteurl}/{page.url}' if siteurl else f'/{page.url}'
        graph = build_graph(page.content or '', page_url, page.title, siteurl)
        nodes = graph['@graph'] if graph else []

        if is_home:
            nodes = [n for n in nodes if n.get('@id') != author_id]
            nodes = absolutise(site_graph, siteurl) + nodes
        elif is_insights:
            articles = page_generator.context.get('articles') or []
            nodes = site_nodes(settings, siteurl,
                               AUTHOR_FRAGMENT, '#organization')
            nodes += insights_nodes(page, articles, settings, siteurl)
        elif extra:
            nodes = [n for n in nodes if n.get('@id') != author_id]
            lead = [person] if person else []
            nodes = absolutise(lead + extra, siteurl) + nodes
            nodes = resolve_references(nodes, absolutise(site_graph, siteurl))

        if not nodes:
            continue

        page.jsonld = to_script_body(
            {'@context': 'https://schema.org', '@graph': nodes})
        count = sum(1 for n in nodes if n.get('@type') == 'ScholarlyArticle')
        logger.info('scholarly: %s node(s), %s publication(s) on %s',
                    len(nodes), count, page.slug)


def register():
    signals.page_generator_finalized.connect(attach)
    signals.article_generator_finalized.connect(attach_articles)
