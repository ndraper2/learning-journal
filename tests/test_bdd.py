# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pytest_bdd import scenario, given, when, then
import pytest

import journal


@pytest.fixture(scope='module')
def db_session(request, connection):
    from transaction import abort
    trans = connection.begin()
    request.addfinalizer(trans.rollback)
    request.addfinalizer(abort)

    from journal import DBSession
    return DBSession


@scenario('features/homepage.feature',
          'The Homepage lists entries for anonymous users')
def test_home_listing_as_anon():
    pass


@given('an anonymous user')
def test_an_anonymous_user(app):
    pass


@given('a list of three entries')
def test_create_entries(db_session):
    title_template = "Title {}"
    text_template = "Entry Text {}"
    for x in range(3):
        journal.Entry.write(
            title=title_template.format(x),
            text=text_template.format(x),
            session=db_session
        )
        db_session.flush()


@when('the user visits the homepage')
def test_homepage(homepage):
    pass


@then('they see a list of three entries')
def test_check_entry_list(homepage):
    html = homepage.html
    entries = html.find_all('article', class_='entry')
    assert len(entries) == 3


@scenario('features/detail.feature',
          'The Detail page displays an entry for an anonymous user')
def test_detail_listing_as_anon():
    pass


@given('a journal entry')
@given('an entry')
def test_create_one_entry(db_session):
    journal.Entry.write(
        title='A Title',
        text='Some text',
        session=db_session
    )
    db_session.flush()


@when('the user visits the detail page for that entry')
def test_visit_detail_page(app):
    pass


@then('they see the one entry')
def test_check_detail_entry(app):
    response = app.get('/detail/4')
    html = response.html
    assert 'A Title', 'Some text' in html


@scenario('features/edit.feature',
          'An authorized user can edit entries')
def test_edit_listing_auth():
    pass


@given('an authenticated user')
def test_authenticated_user(app):
    login_data = {'username': 'admin', 'password': 'secret'}
    app.post('/login', params=login_data, status='*')
    return app


@when('the user visits the edit page')
def test_visit_edit_page(app):
    pass


@then('can edit the title and text of the entry')
def test_edit_entry(test_authenticated_user):
    changed = {'title': 'An Edited Title', 'text': 'some edited text'}
    redirect = test_authenticated_user.post('/edit/4', params=changed)
    response = redirect.follow()
    assert 'An Edited Title', 'some edited text' in response.html
