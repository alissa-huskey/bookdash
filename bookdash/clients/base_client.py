"""Module for web scraping clients that can be operated like API clients."""

from functools import partialmethod

import requests
from bs4 import BeautifulSoup
from more_itertools import first

from bookdash import abort, log

bp = breakpoint

__all__ = ["BaseClient"]


class BaseClient:
    """API client class."""

    AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) "
        "AppleWebKit/601.3.9 (KHTML, like Gecko) "
        "Version/9.0.2 Safari/601.3.9"
    )

    def __init__(self, **kwargs):
        self.responses = []
        self.session = requests.session()
        self.session.headers.update({'user-agent': self.AGENT})

    def request(self, method, url, **kwargs):
        """Make a session request."""
        response = self.session.request(method, url, **kwargs)
        self.responses.append(response)
        if not response.ok:
            abort(
                f"Request to {url} failed:", "\n",
                response.status_code, response.reason
            )
        return response

    get = partialmethod(request, "GET")
    post = partialmethod(request, "POST")
    options = partialmethod(request, "OPTIONS")
    head = partialmethod(request, "HEAD")
    put = partialmethod(request, "PUT")
    patch = partialmethod(request, "PATCH")
    delete = partialmethod(request, "DELETE")
