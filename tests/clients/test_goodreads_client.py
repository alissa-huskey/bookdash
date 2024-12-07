import urllib.parse as url_parse
from functools import partialmethod
import pickle

import pytest
import requests
import requests_mock
from pytest_localserver.http import WSGIServer

from bookdash.clients.goodreads_client import GoodreadsClient
from tests import get_filecontents

bp = breakpoint


class MockGoodreads:
    """Mock goodreads login responses."""

    DISPATCH = {
        "/user/sign_in": "user_signin",
        "/ap/signin": "email_signin",
        "/": "authorize",
    }

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

    def __iter__(self):
        url = self.environ.get("PATH_INFO")
        name = self.DISPATCH.get(url)

        if not name:
            name = "not_found"

        method = getattr(self, name)
        status, headers, contents = method()

        headers = list(headers.items())

        self.start(status, headers)
        yield contents

    def response(self, status, content_type, contents, headers={}):
        """Send a response."""
        headers.update({"Content-type": content_type})
        return status, headers, contents

    def success_response(self, file, headers={}):
        """Send a successful response."""
        contents = get_filecontents(file).encode("utf8")
        return self.response("200 OK", "text/html", contents, headers)

    def authorize(self):
        """Set session-id cookie then respond with success."""
        file = "goodreads-home-authed.html"
        headers = {"Set-Cookie": "session-id=12345"}
        return self.success_response(file, headers)

    user_signin = partialmethod(success_response, "goodreads-user-signin.html")
    email_signin = partialmethod(success_response, "goodreads-email-signin.html")
    not_found = partialmethod(response, "400 Not Found", "text/plain", b"Not found.")



@pytest.fixture
def testserver():
    """Server for app."""
    server = WSGIServer(application=MockGoodreads)
    server.start()
    yield server
    server.stop()


def encode(data: dict) -> str:
    """Encode a URL."""
    return "&".join(
        [f"{url_parse.quote_plus(k)}={url_parse.quote_plus(v)}"
         for k, v in data.items()]
    )


def test_login(testserver, tmp_path):
    """
    WHEN: .login() is called
    THEN: it should log you in and redirect you to the goodreads homepage.
    """

    GoodreadsClient.BASE_URL = testserver.url
    GoodreadsClient.BROWSER_DIR = tmp_path / "browser"
    GoodreadsClient.COOKIES_FILE = tmp_path / "cookies" / "goodreads.pkl"

    api = GoodreadsClient()
    result = api.login("", "") # empty username/pwd to avoid slow typing

    # get the browser's current URL and strip the query string
    url_parts = url_parse.urlparse(result)
    current_url = result.rstrip(f"?{url_parts.query}")

    # ensure we have been redirected back to the home page
    assert current_url == f"{testserver.url}/"
    assert api.cookie_jar.has("session-id")
    assert api.COOKIES_FILE.is_file()


@pytest.mark.parametrize("filecontents", [
    {'filename': "goodreads-search.html"}
], indirect=True)
def test_search(filecontents):  # noqa
    api = GoodreadsClient(title="ender's game")

    with requests_mock.Mocker() as m:
        m.get("https://www.goodreads.com/search", text=filecontents)
        books = api.search()
    response = api.responses[-1]

    params = {'q': "ender's game", 'search[field]': "title"}
    assert response.request.path_url == f"/search?{encode(params)}"
    assert books


@pytest.mark.parametrize("filecontents", [
    {'filename': "goodreads-search.html"}
], indirect=True)
def test_search_title(filecontents):  # noqa
    api = GoodreadsClient(title="ender's game")

    with requests_mock.Mocker() as m:
        m.get("https://www.goodreads.com/search", text=filecontents)
        books = api.search()
    response = api.responses[-1]

    params = {'q': "ender's game", 'search[field]': "title"}
    assert response.request.path_url == f"/search?{encode(params)}"
    assert books


@pytest.mark.parametrize("filecontents", [
    {'filename': "goodreads-search.html"}
], indirect=True)
def test_search_author(filecontents):  # noqa
    api = GoodreadsClient(author="orson scott card")

    with requests_mock.Mocker() as m:
        m.get("https://www.goodreads.com/search", text=filecontents)
        books = api.search()
    response = api.responses[-1]

    params = {'q': "orson scott card", 'search[field]': "author"}
    assert response.request.path_url == f"/search?{encode(params)}"
    assert books


@pytest.mark.parametrize("filecontents", [
    {'filename': "goodreads-search.html"}
], indirect=True)
def test_search_multi(filecontents):  # noqa
    api = GoodreadsClient(title="ender's game", author="orson scott card")

    with requests_mock.Mocker() as m:
        m.get("https://www.goodreads.com/search", text=filecontents)
        books = api.search()
    response = api.responses[-1]

    params = {'q': "ender's game orson scott card", 'search[field]': "all"}
    assert response.request.path_url == f"/search?{encode(params)}"
    assert books
