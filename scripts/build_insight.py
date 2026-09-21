#!/usr/bin/env python3
"""Build one Insight from its canonical sources.

    insights/<slug>/manuscript.tex   scientific prose and \\cite keys
    insights/<slug>/references.bib   the only bibliography
    insights/<slug>/metadata.yaml    everything both outputs state
                 |
                 +--> build/insights/<slug>/<slug>.pdf   (latexmk, for Zenodo)
                 +--> content/insights/<slug>.rst        (Pelican, generated)

The direction is one-way. The generated .rst carries a DO-NOT-EDIT header and
CI fails when it does not match what these sources produce, so a scientific
correction can only be made in the sources.

Reference numbers are never written anywhere. Both outputs derive them from the
order of first citation: biblatex with sorting=none for the PDF, docutils
auto-numbered footnotes (`[#key]_`) for the web.

Usage:
    python3 scripts/build_insight.py <slug> [--web] [--pdf]

With neither flag it builds both.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from datetime import date

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSIGHTS = os.path.join(REPO, 'insights')
TEMPLATES = os.path.join(INSIGHTS, 'templates')
BUILD = os.path.join(REPO, 'build', 'insights')
CONTENT = os.path.join(REPO, 'content', 'insights')

REQUIRED_META = ['title', 'subtitle', 'slug', 'author', 'affiliation', 'date',
                 'modified', 'version', 'series', 'number', 'status',
                 'description', 'summary', 'tags']

# Required additionally before an Insight may go to production. `abstract` is
# here rather than in REQUIRED_META because a draft may not have one yet, but
# nothing is published without the text its deposit record will carry.
REQUIRED_PUBLISHED = ['abstract', 'description', 'summary', 'tags', 'version']

DOI_RE = re.compile(r'^10\.\d{4,9}/\S+$')

# A LaTeX environment becomes `.. container:: <name>`, which is exactly the
# site's one-wrapper-one-class convention. Where the design needs a second
# class, it is added here rather than in the manuscript: presentation stays
# out of the scientific source.
CONTAINER_CLASSES = {
    'chain': 'blueprint chain',
}

# How many authors before the list is cut, and how many survive the cut.
MAX_AUTHORS = 5
KEEP_AUTHORS = 3


class BuildError(Exception):
    pass


def run(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        raise BuildError(f'{cmd[0]} failed:\n{result.stdout}\n{result.stderr}')
    return result.stdout


def need(tool):
    if shutil.which(tool) is None:
        raise BuildError(
            f'{tool} is not installed. The Insight pipeline needs pandoc for '
            f'the web build and a LaTeX toolchain for the PDF.')


def source_dir(slug):
    path = os.path.join(INSIGHTS, slug)
    if not os.path.isdir(path):
        raise BuildError(f'no such Insight: insights/{slug}/')
    return path


def load_metadata(slug):
    path = os.path.join(source_dir(slug), 'metadata.yaml')
    if not os.path.isfile(path):
        raise BuildError(f'missing {os.path.relpath(path, REPO)}')
    with open(path, encoding='utf-8') as f:
        meta = yaml.safe_load(f) or {}

    missing = [k for k in REQUIRED_META if meta.get(k) in (None, '', [])]
    if missing:
        raise BuildError(f'{slug}/metadata.yaml: missing {", ".join(missing)}')

    if meta['slug'] != slug:
        raise BuildError(
            f"{slug}/metadata.yaml: slug is {meta['slug']!r}, but the "
            f"directory is {slug!r}")

    if meta['status'] not in ('draft', 'published'):
        raise BuildError(f"{slug}: status must be draft or published, "
                         f"not {meta['status']!r}")

    if meta['status'] == 'published':
        incomplete = [k for k in REQUIRED_PUBLISHED if not meta.get(k)]
        if incomplete:
            raise BuildError(
                f'{slug}: status is published but {", ".join(incomplete)} '
                f'is incomplete')

    if meta.get('doi') and not DOI_RE.match(str(meta['doi'])):
        raise BuildError(f"{slug}: doi {meta['doi']!r} is not a bare DOI "
                         f"(expected 10.xxxx/...)")

    for field in ('date', 'modified'):
        if not isinstance(meta[field], date):
            raise BuildError(f'{slug}: {field} must be a YYYY-MM-DD date')

    return meta


# --- bibliography ---------------------------------------------------------

def initials(given):
    """"Jörg K. H." -> "JKH"; "Sarah-Luisa J." -> "S-LJ"."""
    out = []
    for part in given.replace('.', ' ').split():
        pieces = [p for p in part.split('-') if p]
        out.append('-'.join(p[0] for p in pieces))
    return ''.join(out)


def format_authors(entry):
    names = []
    for person in entry.get('author', []):
        family = person.get('family', '').strip()
        given = person.get('given', '').strip()
        if not family:
            names.append(person.get('literal', '').strip())
            continue
        names.append(f'{family} {initials(given)}'.strip())
    names = [n for n in names if n]
    if not names:
        return ''
    if len(names) > MAX_AUTHORS:
        names = names[:KEEP_AUTHORS] + ['et al.']
    if names[-1] == 'et al.':
        return ', '.join(names[:-1]) + ', et al.'
    return ', '.join(names)


INLINE_HTML = [
    (re.compile(r'</?i>|</?em>'), '*'),
    (re.compile(r'<sup>([^<]*)</sup>'), r':sup:`\1`'),
    (re.compile(r'<sub>([^<]*)</sub>'), r':sub:`\1`'),
    (re.compile(r'<span class="nocase">([^<]*)</span>'), r'\1'),
]


def rst_escape(text):
    """Bibliography text as RST.

    CSL-JSON keeps the little markup a title needs — italics for a species
    name, superscripts — as HTML. Translate that, and neutralise anything else
    docutils would read as markup.
    """
    text = text.replace('\\', '\\\\').replace('*', r'\*').replace('`', r'\`')
    for pattern, replacement in INLINE_HTML:
        text = pattern.sub(replacement, text)
    return re.sub(r'<[^>]+>', '', text)


def year_of(entry):
    parts = entry.get('issued', {}).get('date-parts', [[]])
    return str(parts[0][0]) if parts and parts[0] else ''


def preprint_keys(bib_path):
    """Keys marked `pubstate = {preprint}`, which CSL-JSON does not carry."""
    with open(bib_path, encoding='utf-8') as f:
        text = f.read()
    keys = set()
    for entry in re.split(r'\n@', text):
        key = re.match(r'\w+\s*\{\s*([^,\s]+)', entry)
        if key and re.search(r'pubstate\s*=\s*[{"]preprint[}"]', entry, re.I):
            keys.add(key.group(1))
    return keys


def load_bibliography(bib_path):
    need('pandoc')
    raw = run(['pandoc', bib_path, '--from=bibtex', '--to=csljson'])
    entries = {}
    for entry in json.loads(raw):
        entries[entry['id']] = entry

    with open(bib_path, encoding='utf-8') as f:
        keys = re.findall(r'^\s*@\w+\s*\{\s*([^,\s]+)', f.read(), re.M)
    duplicates = {k for k in keys if keys.count(k) > 1}
    if duplicates:
        raise BuildError(f'duplicate bibliography keys: '
                         f'{", ".join(sorted(duplicates))}')
    return entries, preprint_keys(bib_path)


def format_entry(entry, is_preprint):
    """One reference, in the house style: authors, title, journal, DOI."""
    bits = []
    authors = format_authors(entry)
    if authors:
        bits.append(authors.rstrip('.') + '.')

    title = rst_escape(entry.get('title', '').strip().rstrip('.'))
    if title:
        bits.append(title + '.')

    venue = rst_escape(entry.get('container-title', '').strip())
    if venue:
        bits.append(f'*{venue}*')

    locator = ''
    volume = str(entry.get('volume', '')).strip()
    issue = str(entry.get('issue', '')).strip()
    pages = str(entry.get('page', '')).replace('-', '\u2013').strip()
    if volume:
        locator = volume
        if issue:
            locator += f'({issue})'
        if pages:
            locator += f':{pages}'
    elif pages:
        locator = pages
    if locator:
        bits.append(locator)

    year = year_of(entry)
    if year:
        bits.append(f'({year}).')

    text = ' '.join(bits).replace(' *', ' *').strip()
    # "*Nature* 505:701-705 (2014)." reads better than "*Nature*, 505 ..."
    text = re.sub(r'\*\s+(\d)', r'* \1', text)

    if is_preprint:
        text += ' Preprint.'

    doi = entry.get('DOI', '').strip()
    if doi:
        text += f'\n`doi:{doi} <https://doi.org/{doi}>`__'
    return text


def render_references(cited, entries, preprints, notes=None):
    """The `.. [#key]` block, in order of first citation.

    A scientific footnote takes its place in the same sequence: one numbering
    for everything the prose points at, which is what a numeric style means.
    """
    notes = notes or {}
    lines = []
    for key in cited:
        if key in notes:
            text = notes[key]
        else:
            text = format_entry(entries[key], key in preprints)
        head, _, tail = text.partition('\n')
        prefix = f'  .. [#{key}] '
        wrapped = textwrap.wrap(head, width=78, initial_indent=' ' * len(prefix),
                                subsequent_indent='     ',
                                break_long_words=False, break_on_hyphens=False)
        wrapped[0] = prefix + wrapped[0].lstrip()
        if tail:
            # The DOI link must not be broken across lines.
            wrapped.append(f'     {tail}')
        lines.append('\n'.join(wrapped))
    return '\n'.join(lines)


# --- LaTeX to reStructuredText -------------------------------------------

CITE_RE = re.compile(r':raw-latex:`\\cite\{([^}]*)\}`')
RAW_LATEX_RE = re.compile(r':raw-latex:`([^`]*)`')
# `[ \t]*`, never `\s*`: with re.M a leading `\s*` happily swallows the
# previous line's newline, and the "indent" then contains a line break.
CONTAINER_RE = re.compile(r'^([ \t]*)\.\. container:: (\S+)[ \t]*$', re.M)


DIRECTIVE_RE = re.compile(r'^\s*\.\.\s+[\w-]+::')
OPTION_LINE_RE = re.compile(r'^\s+:[\w-]+:')


def blank_line_after_directives(body):
    """A directive must be separated from its content by a blank line.

    `--wrap=preserve` keeps the manuscript's own line breaks, which makes the
    generated file diff cleanly against the source — but pandoc then writes the
    container's first paragraph straight under the directive, where docutils
    reads it as further class names rather than as content.
    """
    lines = body.split('\n')
    out = []
    for i, line in enumerate(lines):
        out.append(line)
        if not DIRECTIVE_RE.match(line) or i + 1 >= len(lines):
            continue
        following = lines[i + 1]
        # An option block belongs to the directive: :name:, :width: and the
        # rest must stay attached to it, with no blank line in between.
        if following.strip() and not OPTION_LINE_RE.match(following):
            out.append('')
    return '\n'.join(out)


OPTION_RE = re.compile(r'^([ \t]+)(name|width|height|align|alt|scale): (\S.*)$',
                       re.M)
FOOTNOTE_REF_RE = re.compile(r'\[(\d+)\]_')
FOOTNOTE_DEF_RE = re.compile(r'^\.\. \[(\d+)\]', re.M)
DANGLING_REF_RE = re.compile(r'`\[([^\]]+)\] <#([^>]+)>`__')


def fix_directive_options(body):
    """Pandoc writes a figure's `name` option without its leading colon.

    docutils then reads `name: fig:one` as the first line of the caption, the
    anchor is never created, and every `Figure 1` cross-reference points at
    nothing. Restore the colon on the option lines a figure can carry.
    """
    return OPTION_RE.sub(r'\1:\2: \3', body)


def extract_notes(body):
    """Pull scientific footnotes out of the body, keyed by label.

    Pandoc numbers `\\footnote` by hand — `[1]_` with a `.. [1]` definition
    parked at the end of the body. Two problems follow. docutils numbers
    auto-numbered footnotes by the order of their *definitions*, so a note
    defined before the bibliography would take [1] and push the first
    reference to [2]; and a note sitting outside the reference list is a
    second, competing numbering.

    Both go away if notes and references are one list in order of first
    appearance, which is what a numeric citation style means anyway. The
    definitions come out here and are merged back in citation order.
    """
    body = FOOTNOTE_REF_RE.sub(r'[#fn\1]_', body)
    body = FOOTNOTE_DEF_RE.sub(r'.. [#fn\1]', body)

    notes = {}
    lines = body.split('\n')
    out = []
    i = 0
    while i < len(lines):
        match = re.match(r'^\.\. \[#(fn\d+)\](.*)$', lines[i])
        if not match:
            out.append(lines[i])
            i += 1
            continue
        label, rest = match.groups()
        text = [rest.strip()]
        i += 1
        while i < len(lines) and (not lines[i].strip()
                                  or lines[i].startswith('   ')):
            text.append(lines[i].strip())
            i += 1
        notes[label] = ' '.join(part for part in text if part)
    return '\n'.join(out), notes


MATH_ENV_RE = re.compile(
    r'^\s*\\(?:begin|end)\{(?:equation\*?|displaymath|math)\}\s*$')
LABEL_RE = re.compile(r'\\label\{([^}]*)\}')


def clean_math_blocks(body):
    """Make a display equation something docutils can render.

    `.. math::` is already display maths, but pandoc leaves the LaTeX
    environment inside it, and docutils' MathML converter stops at
    "Environment equation not supported" — which drops the whole article from
    the build. Strip the redundant environment and turn `\\label{}` into the
    directive's `:name:`, which is what creates the anchor.
    """
    lines = body.split('\n')
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if not re.match(r'^\s*\.\. math::\s*$', line):
            i += 1
            continue

        indent = re.match(r'^(\s*)', line).group(1)
        i += 1
        block = []
        while i < len(lines) and (not lines[i].strip()
                                  or lines[i].startswith(indent + ' ')):
            block.append(lines[i])
            i += 1

        names = []
        cleaned = []
        for entry in block:
            if MATH_ENV_RE.match(entry):
                continue
            names += LABEL_RE.findall(entry)
            entry = LABEL_RE.sub('', entry)
            if entry.strip() or not cleaned or cleaned[-1].strip():
                cleaned.append(entry.rstrip())
        while cleaned and not cleaned[-1].strip():
            cleaned.pop()

        if names:
            out.append(f'{indent}   :name: {names[0]}')
        if cleaned and cleaned[0].strip():
            out.append('')
        out.extend(cleaned)
        out.append('')  # separate the block from the paragraph that follows
    return '\n'.join(out)


ANCHOR_LINK_RE = re.compile(r'<#([^>]+)>`__')


def normalise_anchors(body):
    """Point a cross-reference at the id docutils will actually create.

    A LaTeX label is `fig:one`; docutils lowercases and replaces everything
    that is not alphanumeric, giving `fig-one`. Pandoc writes the link with
    the label unchanged, so every figure and table reference would land
    nowhere.
    """
    def fix(match):
        target = re.sub(r'[^a-z0-9]+', '-', match.group(1).lower()).strip('-')
        return f'<#{target}>`__'

    return ANCHOR_LINK_RE.sub(fix, body)


def check_cross_references(slug, body):
    """Fail on a cross-reference the converter could not resolve.

    Pandoc numbers figure and table references, but an equation reference
    survives as a link labelled `[eq:gibbs]` pointing at an anchor that does
    not exist. Better to stop than to publish that.
    """
    dangling = [label for label, target in DANGLING_REF_RE.findall(body)
                if label == target]
    if dangling:
        raise BuildError(
            f'{slug}: unresolved cross-reference(s): '
            f'{", ".join(sorted(set(dangling)))}. The converter numbers '
            f'figures and tables but not equations; refer to the equation in '
            f'prose instead, or make it a numbered figure.')


TABLE_LABEL_RE = re.compile(
    r'\\begin\{table\*?\}(.*?)\\end\{table\*?\}', re.S)
TABLE_DIRECTIVE_RE = re.compile(r'^([ \t]*)\.\. table::(.*)$', re.M)


def name_tables(body, tex):
    """Give each converted table the anchor its `\\label` asked for.

    Pandoc resolves `Table~\\ref{tab:one}` to the number but writes no
    `:name:` on the table itself, so the reference lands nowhere. The labels
    come back from the manuscript, in order: the nth table environment there
    is the nth table directive here.
    """
    labels = labels_in(TABLE_LABEL_RE, tex)
    if not any(labels):
        return body

    index = iter(range(len(labels)))

    def name(match):
        indent, argument = match.groups()
        try:
            label = labels[next(index)]
        except (StopIteration, IndexError):
            return match.group(0)
        if not label:
            return match.group(0)
        return f'{indent}.. table::{argument}\n{indent}   :name: {label}'

    return TABLE_DIRECTIVE_RE.sub(name, body)


FIGURE_LABEL_RE = re.compile(
    r'\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}', re.S)
FIGURE_DIRECTIVE_RE = re.compile(r'^([ \t]*)\.\. figure:: (\S+)[ \t]*$')
NAME_OPTION_RE = re.compile(r'^[ \t]+:?name:', re.I)


def labels_in(pattern, tex):
    """The \\label of each environment matching `pattern`, in document order."""
    labels = []
    for block in pattern.findall(tex):
        found = LABEL_RE.search(block)
        labels.append(found.group(1) if found else None)
    return labels


def name_figures(body, tex):
    """Give each figure the anchor its `\\label` asked for.

    Pandoc's RST writer has emitted a figure's name three different ways
    across versions — as `name:` without the leading colon, as a proper
    `:name:`, and not at all — so none of them can be relied on. The labels
    come from the manuscript instead, in order, exactly as for tables: the nth
    figure environment there is the nth figure directive here.
    """
    labels = labels_in(FIGURE_LABEL_RE, tex)
    if not any(labels):
        return body

    lines = body.split('\n')
    out = []
    index = 0
    i = 0
    while i < len(lines):
        match = FIGURE_DIRECTIVE_RE.match(lines[i])
        if not match:
            out.append(lines[i])
            i += 1
            continue

        indent = match.group(1)
        out.append(lines[i])
        i += 1
        label = labels[index] if index < len(labels) else None
        index += 1
        if label:
            out.append(f'{indent}   :name: {label}')
        # Whatever this pandoc wrote for the name, ours is the one that stays.
        while i < len(lines) and (OPTION_LINE_RE.match(lines[i])
                                  or NAME_OPTION_RE.match(lines[i])):
            if not NAME_OPTION_RE.match(lines[i]):
                out.append(lines[i])
            i += 1
    return '\n'.join(out)


def pandoc_version():
    """The pandoc that produced a build, for the generated file's header.

    The RST writer's output changes between versions, so a file generated by
    one pandoc need not be byte-identical to the same file generated by
    another. Recording it lets the drift check tell a hand edit — which it
    must catch — from a version difference, which is not anyone's mistake.
    """
    need('pandoc')
    first = run(['pandoc', '--version']).splitlines()[0]
    return first.split()[1] if len(first.split()) > 1 else 'unknown'


def convert_body(slug, tex_path):
    need('pandoc')
    body = run(['pandoc', tex_path, '--from=latex', '--to=rst',
                '--wrap=preserve'])
    with open(tex_path, encoding='utf-8') as f:
        tex = f.read()
    body = name_tables(body, tex)
    body = name_figures(body, tex)

    def cite(match):
        keys = [k.strip() for k in match.group(1).split(',') if k.strip()]
        return ' '.join(f'[#{k}]_' for k in keys)

    body = CITE_RE.sub(cite, body)

    leftover = RAW_LATEX_RE.findall(body)
    if leftover:
        raise BuildError(
            f'{slug}: pandoc could not convert these LaTeX constructs, so they '
            f'would reach the website as raw LaTeX: '
            f'{", ".join(sorted(set(leftover)))}. Either express them in a way '
            f'pandoc understands, or teach the build to translate them.')

    def container(match):
        indent, name = match.groups()
        return f'{indent}.. container:: {CONTAINER_CLASSES.get(name, name)}'

    body = CONTAINER_RE.sub(container, body)
    body = fix_directive_options(body)
    body = clean_math_blocks(body)
    body, notes = extract_notes(body)
    body = blank_line_after_directives(body)
    body = normalise_anchors(body)
    check_cross_references(slug, body)

    # One sequence for everything, ordered by first appearance in the prose.
    cited = [label for label in re.findall(r'\[#([\w:-]+)\]_', body)]
    cited = list(dict.fromkeys(cited))
    return body.strip() + '\n', cited, notes


IMAGE_RE = re.compile(r'^([ \t]*)\.\. (figure|image):: (\S+)[ \t]*$', re.M)

# Formats a browser can show. A PDF master is fine for the PDF build, but the
# web needs a sibling in one of these.
WEB_IMAGE_EXT = ('.svg', '.png', '.jpg', '.jpeg', '.webp', '.gif')


def publish_figures(slug, body, out_dir, quiet):
    """Copy the manuscript's figures into the site and repoint the RST at them.

    Same source images for both outputs, as far as the formats allow: the
    figure is declared once, in the manuscript, and the website is served the
    file the author actually drew.
    """
    src = source_dir(slug)
    # out_dir is content/insights, so the content root is one level up and the
    # figures go to content/static/insights/<slug>/, which STATIC_PATHS
    # publishes at /static/insights/<slug>/.
    content_root = os.path.dirname(os.path.abspath(out_dir))
    static = os.path.join(content_root, 'static', 'insights', slug)
    copied = []

    def repoint(match):
        indent, directive, ref = match.groups()
        candidates = [os.path.join(src, ref),
                      os.path.join(src, 'figures', os.path.basename(ref))]
        found = next((c for c in candidates if os.path.isfile(c)), None)

        if found and not found.lower().endswith(WEB_IMAGE_EXT):
            stem = os.path.splitext(found)[0]
            sibling = next((stem + ext for ext in WEB_IMAGE_EXT
                            if os.path.isfile(stem + ext)), None)
            if not sibling:
                raise BuildError(
                    f'{slug}: figure {ref} cannot be shown on the web. Add a '
                    f'{" or ".join(WEB_IMAGE_EXT)} version beside it.')
            found = sibling

        if not found:
            raise BuildError(f'{slug}: figure not found: {ref}')

        name = os.path.basename(found)
        os.makedirs(static, exist_ok=True)
        shutil.copy2(found, os.path.join(static, name))
        copied.append(name)
        return f'{indent}.. {directive}:: /static/insights/{slug}/{name}'

    body = IMAGE_RE.sub(repoint, body)
    if copied and not quiet:
        print(f'figures: {len(copied)} copied to '
              f'content/static/insights/{slug}/')
    return body


def build_web(slug, meta, out_dir=CONTENT, quiet=False):
    src = source_dir(slug)
    body, cited, notes = convert_body(slug, os.path.join(src, 'manuscript.tex'))
    body = publish_figures(slug, body, out_dir, quiet)

    bib_path = os.path.join(src, 'references.bib')
    entries, preprints = load_bibliography(bib_path)

    undefined = [k for k in cited if k not in entries and k not in notes]
    if undefined:
        raise BuildError(f'{slug}: undefined citation key(s): '
                         f'{", ".join(undefined)}')

    uncited = [k for k in entries if k not in cited]
    if not quiet:
        for key in sorted(uncited):
            print(f'warning: {slug}: {key} is in references.bib but never '
                  f'cited', file=sys.stderr)

    references = render_references(cited, entries, preprints, notes)

    import jinja2
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATES),
        keep_trailing_newline=True, trim_blocks=False, lstrip_blocks=False)
    rendered = env.get_template('insight.rst.j2').render(
        meta={**meta,
              'date': meta['date'].isoformat(),
              'modified': meta['modified'].isoformat()},
        body=body, references=references, pandoc=pandoc_version(),
        references_title='References and notes' if notes else 'References')

    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f'{slug}.rst')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(rendered)
    if not quiet:
        print(f'web: {os.path.relpath(out, REPO)} '
              f'({len(cited)} reference(s), status {meta["status"]})')
    return out


# --- PDF ------------------------------------------------------------------

def citation_line(meta):
    parts = [f"{meta['author']}.", f"{meta['title']}:", f"{meta['subtitle']}."]
    parts.append(f"{meta['series']} {meta['number']} ({meta['date'].year}).")
    if meta.get('doi'):
        parts.append(f"doi:{meta['doi']}")
    return ' '.join(parts)


def write_deposit_metadata(slug, meta, out_dir):
    """The Zenodo record's fields, next to the PDF they belong to.

    Written out rather than printed because the abstract is a paragraph, and
    retyping bibliographic metadata into a web form is how a deposit and a
    website start disagreeing. Everything here comes from metadata.yaml.

    Note the affiliation: the deposit takes the formal one, naming the
    registered seat, not the title page's fuller geography.

    The related work is the website, as a variant form: both are rendered
    from one manuscript, and the HTML page is the canonical one. It is not
    "is identical to", which DataCite reserves for the same resource
    registered twice.
    """
    url = f'https://rnaforecast.com/insights/{slug}/'
    doi = meta.get('doi') or ('— reserve one on Zenodo, then put it in '
                              'metadata.yaml and rebuild')
    lines = [
        f'Title: {meta["title"]}: {meta["subtitle"]}',
        f'Authors: {meta["author"]} '
        f'({meta.get("affiliation_formal") or meta["affiliation"]})',
        f'Publication date: {meta["date"].isoformat()}',
        f'Version: {meta["version"]}',
        f'Resource type: {meta.get("resource_type", "Publication")}',
        f'Publisher: {meta.get("publisher", "")}',
        f'License: {meta.get("license", "")}',
        f'Copyright: {meta.get("copyright", "")}',
        f'Keywords: {", ".join(meta["tags"])}',
        f'Related work: Is variant form of — {url} (scheme: URL)',
        f'DOI: {doi}',
        '',
        'Description:',
        meta.get('abstract') or meta.get('summary', ''),
    ]
    path = os.path.join(out_dir, 'zenodo.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines).rstrip() + '\n')
    return path


def build_pdf(slug, meta):
    for tool in ('latexmk', 'pdflatex', 'bibtex'):
        need(tool)

    src = source_dir(slug)
    out_dir = os.path.join(BUILD, slug)
    os.makedirs(out_dir, exist_ok=True)

    for name in ('manuscript.tex', 'references.bib'):
        shutil.copy2(os.path.join(src, name), os.path.join(out_dir, name))
    figures = os.path.join(src, 'figures')
    if os.path.isdir(figures):
        shutil.copytree(figures, os.path.join(out_dir, 'figures'),
                        dirs_exist_ok=True)

    with open(os.path.join(TEMPLATES, 'insight.tex'), encoding='utf-8') as f:
        wrapper = f.read()

    doi = meta.get('doi')
    tokens = {
        'TITLE': meta['title'],
        'SHORTTITLE': meta['title'],
        'SUBTITLE': meta['subtitle'],
        'AUTHOR': meta['author'],
        'AFFILIATION': meta['affiliation'],
        'SERIES': meta['series'],
        'NUMBER': str(meta['number']),
        'VERSION': str(meta['version']),
        'DATELONG': meta['date'].strftime('%-d %B %Y'),
        'KEYWORDS': ', '.join(meta['tags']),
        'DOILINE': (f"\\\\\nDOI: \\href{{https://doi.org/{doi}}}{{{doi}}}"
                    if doi else ''),
        # The copyright statement already names the licence, so printing the
        # bare licence as well would say it twice.
        'RIGHTSLINE': (f"\\\\\n{meta.get('copyright') or meta.get('license')}"
                       if (meta.get('copyright') or meta.get('license'))
                       else ''),
        'CITATION': citation_line(meta),
    }
    for key, value in tokens.items():
        wrapper = wrapper.replace(f'%%{key}%%', value)

    main = os.path.join(out_dir, 'main.tex')
    with open(main, 'w', encoding='utf-8') as f:
        f.write(wrapper)

    try:
        run(['latexmk', '-pdf', '-bibtex', '-interaction=nonstopmode',
             '-halt-on-error', '-quiet', 'main.tex'], cwd=out_dir)
    except BuildError as exc:
        log = os.path.join(out_dir, 'main.log')
        tail = ''
        if os.path.isfile(log):
            with open(log, encoding='utf-8', errors='replace') as f:
                tail = '\n'.join(f.read().splitlines()[-40:])
        raise BuildError(f'{exc}\n--- main.log (tail) ---\n{tail}')

    produced = os.path.join(out_dir, 'main.pdf')
    final = os.path.join(out_dir, f'{slug}.pdf')
    shutil.move(produced, final)

    with open(os.path.join(out_dir, 'main.blg'), encoding='utf-8',
              errors='replace') as f:
        blg = f.read()
    for line in blg.splitlines():
        if "didn't find a database entry" in line or 'Warning--' in line:
            print(f'warning: {slug}: bibtex: {line.strip()}', file=sys.stderr)

    print(f'pdf: {os.path.relpath(final, REPO)}')
    deposit = write_deposit_metadata(slug, meta, out_dir)
    print(f'zenodo: {os.path.relpath(deposit, REPO)}')
    if not meta.get('doi'):
        print('zenodo: no DOI reserved yet — add it to metadata.yaml and '
              'rebuild before depositing')
    return final


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slug')
    parser.add_argument('--web', action='store_true')
    parser.add_argument('--pdf', action='store_true')
    args = parser.parse_args()

    both = not (args.web or args.pdf)
    try:
        meta = load_metadata(args.slug)
        if args.web or both:
            build_web(args.slug, meta)
        if args.pdf or both:
            build_pdf(args.slug, meta)
    except BuildError as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
