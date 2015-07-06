# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pytest_bdd import scenario, given, when, then
import pytest
import markdown

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
def an_anonymous_user(app):
    pass


@given('a list of three entries')
def create_entries(db_session):
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
def homepage(homepage):
    pass


@then('they see a list of three entries')
def check_entry_list(homepage):
    html = homepage.html
    entries = html.find_all('article', class_='entry')
    assert len(entries) == 3


@scenario('features/detail.feature',
          'The Detail page displays an entry for an anonymous user')
def test_detail_listing_as_anon():
    pass


@given('a journal entry')
@given('an entry')
def create_one_entry(db_session):
    journal.Entry.write(
        title='A Title',
        text='Some text',
        session=db_session
    )
    db_session.flush()


@when('the user visits the detail page for that entry')
def visit_detail_page(app):
    pass


@then('they see the one entry')
def check_detail_entry(app):
    response = app.get('/detail/4')
    html = response.html
    assert 'A Title', 'Some text' in html


@scenario('features/edit.feature',
          'An authorized user can edit entries')
def test_edit_listing_auth():
    pass


@given('an authenticated user')
def authenticated_user(app):
    login_data = {'username': 'admin', 'password': 'secret'}
    app.post('/login', params=login_data, status='*')
    return app


@when('the user visits the edit page')
def visit_edit_page(app):
    pass


@then('they can edit the title and text of the entry')
def edit_entry(authenticated_user):
    changed = {'title': 'An Edited Title', 'text': 'some edited text'}
    redirect = authenticated_user.post('/edit/5', params=changed)
    response = redirect.follow()
    assert 'An Edited Title', 'some edited text' in response.html


@scenario('features/markdown.feature',
          'An authorized user can use Markdown in an entry')
def test_markdown_entry():
    pass


@when('the user creates an entry')
def create_an_entry_with_markdown(authenticated_user):
    title = 'Markdown Test Title'
    text = """#This is a header 1.
This is a code block:
```python
def x():
    return 'foo'
```
"""
    # gotta add markdown here, since the function's being called in the
    # template, and TestApp isn't going that far
    text = markdown.markdown(text, extensions=['codehilite',
        'fenced_code'])
    authenticated_user.post('/add', params={'title': title, 'text': text})


@then('they can use Markdown to format the entry')
def confirm_markdown_in_entry(app):
    response = app.get('/detail/6')
    assert '<h1>This is a header 1', '<pre>' in response.html


@scenario('features/codehilite.feature',
          'Code blocks are properly highlighted')
def test_codehilite_entry():
    pass


@given('an entry with a code block')
def an_entry_with_a_code_block(app):
    return app.get('/detail/6')


@when('they view the post')
def view_the_post():
    pass


@then('the code block has syntax highlighting')
def check_highlighting(an_entry_with_a_code_block):
    body = an_entry_with_a_code_block.body
    assert '<span class="k">' in body
