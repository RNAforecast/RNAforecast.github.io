"""The training page: stable anchors, waitlists that post where they should,
and nothing that claims a course is bookable."""

import re

from conftest import nodes_of, read
from scripts.check_build import formsubmit_endpoint

PAGE = 'training/index.html'


def test_the_anchors_michaelwolfinger_com_links_to_exist(site):
    html = read(site / PAGE)
    for anchor in ('viennarna', 'local-ai-tools', 'waitlist'):
        assert f'id="{anchor}"' in html, anchor


def test_each_waitlist_form_is_complete(site):
    html = read(site / PAGE)
    forms = re.findall(r'<form\b.*?</form>', html, re.S)
    assert len(forms) == 2
    topics = set()
    for form in forms:
        assert f'action="https://formsubmit.co/{formsubmit_endpoint()}"' in form
        assert 'name="_next" value="https://rnaforecast.com/waitlist/"' in form
        assert 'name="_autoresponse"' in form
        assert 'name="_honey"' in form
        assert 'type="email"' in form and 'required' in form
        topics.add(re.search(r'name="topic" value="([^"]+)"', form).group(1))
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


def test_the_endpoint_setting_rewrites_every_form():
    """Content keeps the readable address; the build routes to the setting."""
    from plugins.semantics import route_forms
    html = ('<form action="https://formsubmit.co/hello@rnaforecast.com">'
            '<form action="https://formsubmit.co/hello@rnaforecast.com">')
    routed, count = route_forms(html, 'a1b2c3d4e5f6')
    assert count == 2
    assert routed.count('action="https://formsubmit.co/a1b2c3d4e5f6"') == 2
    assert '@' not in routed
    same, count = route_forms(html, 'hello@rnaforecast.com')
    assert same == html and count == 0
