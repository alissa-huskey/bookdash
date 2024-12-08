import pytest
import requests
from pytest_localserver.http import WSGIServer


def make_request(url):
    """Make a web request and return the text content."""
    response = requests.get(url)
    return response.text


class SimpleApp:
    """App to respond with success."""

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

    def __iter__(self):
        status = "200 OK"
        response_headers = [("Content-type","text/plain")]
        self.start(status, response_headers)
        yield b"success"


def simple_app(environ, start_response):
    """Respond with success."""
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    start_response(status, response_headers)
    return ["success".encode("utf-8")]


@pytest.fixture
def testserver(request):
    """Server for app."""
    app = request.param
    server = WSGIServer(application=app)
    server.start()
    yield server
    server.stop()


def test_make_request_httpserver(httpserver):
    """Test request_app() using the httpserver fixture."""
    httpserver.serve_content(
        content="success",
        code=200,
    )

    assert make_request(httpserver.url) == "success"


@pytest.mark.parametrize("testserver", [simple_app, SimpleApp], indirect=True)
def test_make_request_app(testserver):
    """Test request_app() using an app function or class function."""
    assert make_request(testserver.url) == "success"
