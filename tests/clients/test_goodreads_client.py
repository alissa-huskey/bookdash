import urllib.parse as url

import pytest
import requests
import requests_mock

from bookdash.clients.goodreads_client import GoodreadsClient

bp = breakpoint


def encode(data: dict) -> str:
    """Encode a URL."""
    return "&".join(
        [f"{url.quote_plus(k)}={url.quote_plus(v)}"
         for k, v in data.items()]
    )


@pytest.mark.skip("need to rewrite--goodreads changed their auth process")
@pytest.mark.parametrize("filecontents", [
    {'filename': "goodreads-signin.html"}
], indirect=True)
def test_login(filecontents):  # noqa
    """."""


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



