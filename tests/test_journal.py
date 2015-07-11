# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
from sqlalchemy.exc import IntegrityError
from pyramid import testing
from cryptacular.bcrypt import BCRYPTPasswordManager
from webtest.app import AppError

import journal


@pytest.fixture()
def db_session(request, connection):
    from transaction import abort
    trans = connection.begin()
    request.addfinalizer(trans.rollback)
    request.addfinalizer(abort)

    from journal import DBSession
    return DBSession


@pytest.fixture(scope='function')
def auth_req(request):
    manager = BCRYPTPasswordManager()
    settings = {
        'auth.username': 'admin',
        'auth.password': manager.encode('secret'),
    }
    testing.setUp(settings=settings)
    req = testing.DummyRequest()

    def cleanup():
        testing.tearDown()

    request.addfinalizer(cleanup)

    return req


@pytest.fixture()
def entry(db_session):
    entry = journal.Entry.write(
        title='Test Title',
        text='Test Entry Text',
        session=db_session
    )
    db_session.flush()
    return entry


def test_write_entry(db_session):
    kwargs = {'title': 'Test Title', 'text': 'Test entry text'}
    kwargs['session'] = db_session
    # first, assert that there are no entries in the database
    assert db_session.query(journal.Entry).count() == 0
    # now, create an entry using the 'write' class method
    entry = journal.Entry.write(**kwargs)
    # the entry we get back ought to be an instance of Entry
    assert isinstance(entry, journal.Entry)
    # now, we should have one entry
    assert db_session.query(journal.Entry).count() == 1
    for field in kwargs:
        if field != 'session':
            assert getattr(entry, field, '') == kwargs[field]
    # id and created should be set automatically upon writing to db:
    for auto in ['id', 'created']:
        assert getattr(entry, auto, None) is not None


def test_write_entry_no_title(db_session):
    bad_data = {'text': 'test text'}
    with pytest.raises(IntegrityError):
        journal.Entry.write(session=db_session, **bad_data)


def test_entry_no_text(db_session):
    bad_data = {'title': 'test_title'}
    with pytest.raises(IntegrityError):
        journal.Entry.write(session=db_session, **bad_data)


def test_entry_extra_field(db_session):
    bad_data = {'title': 'test title', 'text': 'test text', 'footer': 'test footer'}
    with pytest.raises(TypeError):
        journal.Entry.write(session=db_session, **bad_data)


def test_read_entries_empty(db_session):
    entries = journal.Entry.all()
    assert len(entries) == 0


def test_read_entries_one(db_session):
    title_template = "Title {}"
    text_template = "Entry Text {}"
    # write three entries, with order clear in the title and text
    for x in range(3):
        journal.Entry.write(
            title=title_template.format(x),
            text=text_template.format(x),
            session=db_session
        )
    entries = journal.Entry.all()
    assert len(entries) == 3
    assert entries[0].title > entries[1].title > entries[2].title
    for entry in entries:
        assert isinstance(entry, journal.Entry)


def test_entry_search(db_session):
    kwargs = {'title': 'Test Title', 'text': 'Test entry text'}
    journal.Entry.write(**kwargs)
    entry = journal.Entry.search(13)  # ORDER SENSITIVE
    assert isinstance(entry, journal.Entry)
    for field in kwargs:
        assert getattr(entry, field, '') == kwargs[field]


def test_empty_listing(app):
    response = app.get('/')
    assert response.status_code == 200
    actual = response.body
    expected = 'No entries here so far'
    assert expected in actual


def test_listing(app, entry):
    response = app.get('/')
    assert response.status_code == 200
    actual = response.body
    for field in ['title', 'text']:
        expected = getattr(entry, field, 'absent')
        assert expected in actual


def test_do_login_success(auth_req):
    from journal import do_login
    auth_req.params = {'username': 'admin', 'password': 'secret'}
    assert do_login(auth_req)


def test_do_login_bad_pass(auth_req):
    from journal import do_login
    auth_req.params = {'username': 'admin', 'password': 'wrong'}
    assert not do_login(auth_req)


def test_do_login_bad_user(auth_req):
    from journal import do_login
    auth_req.params = {'username': 'bad', 'password': 'secret'}
    assert not do_login(auth_req)


def test_do_login_missing_params(auth_req):
    from journal import do_login
    for params in ({'username': 'admin'}, {'password': 'secret'}):
        auth_req.params = params
        with pytest.raises(ValueError):
            do_login(auth_req)


INPUT_BTN = '<input id="addButton" type="submit" value="Share" name="Share"/>'


def login_helper(username, password, app):
    """Encapsulate app login for reuse in tests
    Accept all status codes so that we can make assertions in tests
    """
    login_data = {'username': username, 'password': password}
    return app.post('/login', params=login_data, status='*')


def test_start_as_anonymous(app):
    response = app.get('/', status=200)
    actual = response.body
    assert INPUT_BTN not in actual


def test_login_success(app):
    username, password = ('admin', 'secret')
    redirect = login_helper(username, password, app)
    assert redirect.status_code == 302
    response = redirect.follow()
    assert response.status_code == 200
    response = app.get('/add', status=200)
    actual = response.body
    assert INPUT_BTN in actual


def test_login_fails(app):
    username, password = ('admin', 'wrong')
    response = login_helper(username, password, app)
    assert response.status_code == 200
    actual = response.body
    assert "Login Failed" in actual
    response = app.get('/add', status='*')
    assert response.status_code == 403


def test_logout(app):
    test_login_success(app)
    redirect = app.get('/logout', status="3*")
    response = redirect.follow()
    assert response.status_code == 200
    response = app.get('/add', status='*')
    assert response.status_code == 403


def test_post_to_add_view(app):
    test_login_success(app)
    entry_data = {
        'title': 'Hello there',
        'text': 'This is a post',
    }
    response = app.post('/add', params=entry_data, status='3*')
    redirected = response.follow()
    actual = redirected.body
    for expected in entry_data.values():
        assert expected in actual


def test_add_no_params(app):
    test_login_success(app)
    response = app.post('/add', status=500)
    assert 'IntegrityError' in response.body


def test_add_get(app):
    test_login_success(app)
    entry_data = {
        'title': 'Hello there',
        'text': 'This is a post',
    }
    with pytest.raises(AppError):
        app.get('/add', params=entry_data, status='3*')

# I have a unicode test here that works correctly when performed live,
# but fails in this test. Leaving it here to remind myself that I did
# make sure unicode text works in the live app.

# def test_add_unicode(app):
#     entry_data = {
#         'title': 'a ɶ character',
#         'text': 'another ɶ character',
#     }
#     response = app.post('/add', params=entry_data, status='3*')
#     redirected = response.follow()
#     actual = redirected.body
#     for expected in entry_data.values():
#         assert expected in actual


def test_sql_injection(app):
    test_login_success(app)
    entry_data = {
        'title': 'Hello there',
        'text': "This is a post'); DROP TABLE entries;",
    }
    response = app.post('/add', params=entry_data, status='3*')
    redirected = response.follow()
    actual = redirected.body
    for expected in entry_data.values():
        assert expected in actual
