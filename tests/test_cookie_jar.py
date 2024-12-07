from datetime import datetime
import pickle

import pytest
import requests

from bookdash.cookie_jar import CookieJar

bp = breakpoint


@pytest.fixture
def now():
    """Return the current timestamp."""
    return datetime.today().timestamp()


def test_cookie_jar():
    assert CookieJar()


@pytest.mark.parametrize(("modifier", "expected"), [
    (1, False), (-1, True), (0, True)
])
def test_cookie_jar_expired(now, modifier, expected):
    """
    GIVEN: a cookie jar populated with cookies
    WHEN: .expired is called
    THEN: it should return True if any are expired, False otherwise
    """
    cookie = {"name": "a-cookie", "expiry": now + modifier}
    jar = CookieJar([cookie])

    assert jar.expired() is expected


@pytest.mark.parametrize(("names", "expected"), [
    (["a-cookie"], True),
    (["no-cooke"], False),
    (["a-cookie", "no-cookie"], False),
])
def test_cookie_jar_has(now, names, expected):
    """
    GIVEN: a cookie jar populated with cookies
    WHEN: .has() is called with one or more cookie names
    THEN: it should return True if all names are present
    OR: it should return False if any are missing
    """
    cookie = {"name": "a-cookie", "value": "12345"}
    jar = CookieJar([cookie])

    assert jar.has(*names) is expected


def test_cookie_jar_cookies_setter():
    """
    GIVEN: a list of cookie dictionaries
    WHEN: .cookies = cookies_list is called
    THEN: .cookies should return a dictionary keyed by cookie name.
    """
    cookie = {"name": "language", "value": "en"}
    jar = CookieJar([cookie])

    assert jar.cookies == {"language": cookie}



def test_validate_cookies(tmp_path):
    """
    GIVEN: a list of cookies where at least one is expired
    WHEN: .validate_cookies() is called
    THEN: False should be returned if any of the cookies are expired
    AND: False should be returned if there is no session-id cookie
    AND: True should be returned otherwise
    """


def test_validate_cookies(tmp_path):
    """
    GIVEN: a list of cookies where at least one is expired
    WHEN: .validate_cookies() is called
    THEN: False should be returned if any of the cookies are expired
    AND: False should be returned if there is no session-id cookie
    AND: True should be returned otherwise
    """


def test_cookie_jar_load(tmp_path):
    """
    GIVEN: a pickled file containing
    WHEN: .load_cookies() is called
    THEN: the cookies should unpickled from the file
    AND: they should be saved at .cookies
    AND: they should be returned
    """

    cookies_file = tmp_path / "goodreads.pkl"

    cookie = {"name": "session-id", "value": "54321"}
    expected = {"session-id": cookie}
    jar = CookieJar([cookie], file=cookies_file)

    with open(cookies_file, "wb") as f:
        pickle.dump(jar.cookies, f)

    result = jar.load()

    assert result == expected
    assert jar.cookies == expected


def test_save_cookies(tmp_path):
    """
    GIVEN: A CookieJar object
    WHEN: .save() is called
    THEN: the cookies should be pickled and saved
    """

    cookies_file = tmp_path / "cookies" / "goodreads.pkl"
    cookies = {"session-id": {"name": "session-id", "value": "54321"}}

    jar = CookieJar(cookies, file=cookies_file)
    jar.save()

    with open(cookies_file, "rb") as f:
        result = pickle.load(f)

    assert cookies_file.is_file()
    assert result == cookies


def test_cookie_jar_for_session():
    """
    GIVEN: a CookieJar with a list of cookies
    WHEN: .for_session() is called with a requests session
    THEN: it should remove the key "sameSite" from the cookies
    AND: it should change "httpOnly": value to "rest": {"httpOnly": value}
    AND: it should rename the "expiry" key to "expires"
    AND: it should return a list of modified keys
    AND: it should add those keys to the session
    """

    cookies = [
        {"name": "a", "value": "1", "expiry": "1733534854"},
        {"name": "b", "value": "2", "httpOnly": "true"},
        {"name": "c", "value": "3", "sameSite": "Strict"},

    ]
    prepared_cookies = [
        {"name": "a", "value": "1", "expires": "1733534854"},
        {"name": "b", "value": "2", "rest": {"httpOnly": "true"}},
        {"name": "c", "value": "3"},

    ]

    session = requests.session()
    jar = CookieJar(cookies)
    result = jar.for_session(session)

    assert result == prepared_cookies
    assert session.cookies.get_dict() == {"a": "1", "b": "2", "c": "3"}


@pytest.mark.parametrize(("name", "modifier", "expected"), [
    ("a-cookie", 1, True),
    ("a-cookie", -1, False),
    ("no-cooke", 1, False),
    ("no-cooke", -1, False),
])
def test_cookie_jar_ok(now, name, modifier, expected):
    """
    GIVEN: a cookie jar populated with cookies
    WHEN: .ok() is called with one or more cookie names
    THEN: it should return True if no cookies are expired and all names are present
    OR: it should return False if any cookies are expired or any names are missing
    """
    cookie = {"name": "a-cookie", "value": "12345", "expiry": now + modifier}
    jar = CookieJar([cookie])

    assert jar.ok(name) is expected
