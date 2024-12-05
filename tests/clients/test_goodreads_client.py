import urllib.parse as url_parse

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
        "/user/sign_in": "goodreads-user-signin.html",
        "/ap/signin": "goodreads-email-signin.html",
        "/": "goodreads-home-authed.html",
    }

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

    def __iter__(self):
        url = self.environ.get("PATH_INFO")
        file = self.DISPATCH.get(url)

        if not file:
            status = "400 Not found"
            response_headers = [("Content-type","text/plain")]
            contents = b"Not found."
        else:
            status = "200 OK"
            response_headers = [("Content-type","text/html")]
            contents = get_filecontents(file).encode("utf8")

            self.start(status, response_headers)
            yield contents


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


def test_login(testserver):
    """
    WHEN: .login() is called
    THEN: it should log you in and redirect you to the goodreads homepage.
    """
    GoodreadsClient.BASE_URL = testserver.url
    api = GoodreadsClient()
    result = api.login("", "")

    # get the browser's current URL and strip the query string
    url_parts = url_parse.urlparse(result)
    current_url = result.rstrip(f"?{url_parts.query}")

    # ensure we have been redirected back to the home page
    assert current_url == f"{GoodreadsClient.BASE_URL}/"


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
