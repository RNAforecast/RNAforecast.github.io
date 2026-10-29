"""The training page: stable anchors, waitlists that post where they should,
and nothing that claims a course is bookable."""

import re

from conftest import nodes_of, read
from scripts.check_build import form_handler

PAGE = 'training/index.html'


def test_the_anchors_michaelwolfinger_com_links_to_exist(site):
    html = read(site / PAGE)
    for anchor in ('viennarna', 'local-ai-tools', 'waitlist'):
        assert f'id="{anchor}"' in html, anchor


WAITLIST_SELECTS = {
    'role': ['experimental-lab', 'computational-group', 'biotech-industry',
             'doctoral-programme', 'tool-developer', 'other'],
    'format': ['remote', 'on-site', 'either'],
    'group': ['just-me', '2-5', '6-12', 'more-than-12'],
}


def test_each_waitlist_form_is_complete(site):
    html = read(site / PAGE)
    forms = re.findall(r'<form\b.*?</form>', html, re.S)
    assert len(forms) == 2
    topics = set()
    for form in forms:
        topic = re.search(r'name="topic" value="([^"]+)"', form).group(1)
        topics.add(topic)
        assert f'action="{form_handler()}/rnaf-waitlist-{topic}"' in form
        # The handler redirects back to this id on a rejected post.
        assert f'class="form-error" id="{topic}-error"' in form
        assert 'name="_honey"' in form
        assert 'type="email"' in form and 'required' in form
        # one required field, the address; everything else is optional and
        # an enum, so the list can be sorted without reading free text
        assert len(re.findall(r'\srequired[\s/>]', form)) == 1, 'only the address is required'
        for name, values in WAITLIST_SELECTS.items():
            select = re.search(rf'<select[^>]*name="{name}"[^>]*>(.*?)</select>', form, re.S)
            assert select, f'no <select name="{name}">'
            assert re.findall(r'value="([^"]+)"', select.group(1)) == values
            assert 'required' not in select.group(0)
        for name in ('name', 'organization'):
            assert re.search(rf'<input[^>]*name="{name}"[^>]*>', form)
        # FormSubmit's options are gone with FormSubmit; the handler owns them.
        assert not re.search(r'name="_(next|subject|template|autoresponse|captcha)"', form)
        assert 'hello&#64;rnaforecast.com</a>' in form, 'no fallback address'
    assert topics == {'viennarna', 'local-ai-tools'}


def test_nothing_is_bookable_yet(site):
    """Both formats are in preparation; the page must not say otherwise."""
    html = read(site / PAGE).lower()
    for word in ('book now', 'register now', 'price', '€', 'eur '):
        assert word not in html, word
    assert 'in preparation' in html


def test_the_courses_are_described_without_an_offer(site):
    courses = nodes_of(site / PAGE, 'Course')
    assert {c['@id'] for c in courses} == {
        'https://rnaforecast.com/training/#viennarna',
        'https://rnaforecast.com/training/#local-ai-tools'}
    for course in courses:
        assert 'offers' not in course and 'hasCourseInstance' not in course
        assert course['provider']['@id'] == 'https://rnaforecast.com/#organization'


def test_the_confirmation_page_is_unlisted(site):
    html = read(site / 'waitlist' / 'index.html')
    assert 'noindex' in html
    assert 'waitlist' not in read(site / 'sitemap.xml')


def test_the_handler_setting_rewrites_every_form():
    """Content writes the production handler; a preview is one setting away."""
    from plugins.semantics import route_forms
    html = ('<form action="https://forms.rnaforecast.com/rnaf-contact">'
            '<form action="https://forms.rnaforecast.com/rnaf-waitlist-viennarna">')
    routed, count = route_forms(html, 'https://form-handler-preview.example.workers.dev/')
    assert count == 2
    assert 'action="https://form-handler-preview.example.workers.dev/rnaf-contact"' in routed
    assert 'action="https://form-handler-preview.example.workers.dev/rnaf-waitlist-viennarna"' in routed
    same, count = route_forms(html, 'https://forms.rnaforecast.com')
    assert same == html and count == 0
