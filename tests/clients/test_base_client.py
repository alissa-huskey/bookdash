import urllib.parse as url

import pytest
import requests
import requests_mock

from bookdash.clients.base_client import BaseClient

bp = breakpoint


def encode(data: dict) -> str:
    """Encode a URL."""
    return "&".join(
        [f"{url.quote_plus(k)}={url.quote_plus(v)}"
         for k, v in data.items()]
    )


def test_init():
    api = BaseClient()
    assert isinstance(api.session, requests.sessions.Session)
    assert api.session.headers.get("user-agent", "").startswith("Mozilla")


@pytest.mark.parametrize("filecontents", [
    {'filename': "todo.json"}
], indirect=True)
def test_request(filecontents):  # noqa
    headers = {
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) "
                      "AppleWebKit/601.3.9 (KHTML, like Gecko) "
                      "Version/9.0.2 Safari/601.3.9"
    }
    api = BaseClient()
    url = "https://jsonplaceholder.typicode.com/todos/1"

    with requests_mock.Mocker() as m:
        m.get(url, text=filecontents)
        response = api.request("GET", url, headers=headers)

    assert response.request.method == "GET"
    assert response.request.url == url
    assert response.request.headers["user-agent"] == headers["user-agent"], \
        "all kwargs are forwarded to the request call"
    assert api.responses[-1] == response, \
        "response is appended to the api.responses list"


@pytest.mark.parametrize("filecontents", [
    {'filename': "todo.json"}
], indirect=True)
def test_partial(filecontents):  # noqa
    api = BaseClient()
    with requests_mock.Mocker() as m:
        m.get("https://jsonplaceholder.typicode.com/todos/1",
              text=filecontents)
        response = api.get("https://jsonplaceholder.typicode.com/todos/1")
    assert response.text == filecontents


@pytest.mark.skip("""need to refactor to raise exception instead of exiting""")
@pytest.mark.parametrize("filecontents", [
    {'filename': "todo.json"}
], indirect=True)
def test_failed_request(filecontents):
    ...


@pytest.mark.skip("need to refactor to raise exception instead of exiting")
def test_failed_login():
    ...


@pytest.mark.skip("need to figure out what this should do")
def test_search_no_results():
    ...


@pytest.mark.skip("need to refactor the matching code out")
def test_search_matches():
    ...


@pytest.mark.skip("need to figure out how ot test this")
def test_search_with_save():
    ...


@pytest.mark.skip("need to figure out what this should do")
def test_search_query():
    ...
