"""Module for web scraping clients that can be operated like API clients."""

from functools import partialmethod

import requests
from more_itertools import first

from . import abort, log
from .books import Book
from .elements.element import Element

__all__ = ["Client"]


class Client:
    """Goodreads client."""

    AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) " \
            "AppleWebKit/601.3.9 (KHTML, like Gecko) " \
            "Version/9.0.2 Safari/601.3.9"

    def __init__(self, **kwargs):
        """Create session.

        Params
        ------
        title (str): title to filter by
        author (str): author to filter by
        series (str): series to filter by
        query (str): submit query and return all results
        save (bool): save response content for debugging
        """
        self.responses = []
        self.session = requests.session()
        self.session.headers.update({'user-agent': self.AGENT})

        self.save = kwargs.pop("save", False)

        self.query = {key: val for key, val in kwargs.items()
                      if val and key in ("query", "title", "author", "series")}

        self.search_by = "all"

        attrs = self.query.keys()
        if len(attrs) == 1 and first(attrs) in ["title", "author"]:
            self.search_by = first(attrs)

    def request(self, method, url, **kwargs):
        """Make a session request."""
        response = self.session.request(method, url, **kwargs)
        self.responses.append(response)
        if not response.ok:
            abort(f"Request to {url} failed:", "\n", response.status_code,
                  response.reason)
        return response

    get = partialmethod(request, "GET")
    post = partialmethod(request, "POST")
    options = partialmethod(request, "OPTIONS")
    head = partialmethod(request, "HEAD")
    put = partialmethod(request, "PUT")
    patch = partialmethod(request, "PATCH")
    delete = partialmethod(request, "DELETE")

    def login(self, email, password):
        """Login to goodreads."""
        response = self.get("https://www.goodreads.com/user/sign_in")
        doc = Element(response.text)
        form = doc.first('//*[@id="emailForm"]/form/fieldset')

        if form is None:
            abort("Login form not found")

        # populate post data from signin page form fields
        data = {field.name: field.value for field in form.xpath('//input')
                if not field.name.startswith("user")}
        data.update({
            'user[email]': email,
            'user[password]': password,
        })

        return self.session.post(
            "https://www.goodreads.com/user/sign_in",
            data=data,
        )

    def search(self) -> list:
        """Submit a query to goodreads and return a list of Book objects.

        Examples
        --------
        >>> api = Client(title="ender's game", author="orson scott card")
        >>> api.search()
        [Book('Ender’s Game')]
        """
        query = " ".join(self.query.values())
        response = self.get(
            "https://www.goodreads.com/search",
            params={'q': query, 'search[field]': self.search_by}
        )

        # log(path_url=response.request.path_url)
        log(url=response.url)
        log(
            prefix="Client.search() query:", query=query,
            search_by=self.search_by
        )

        doc = Element(response.text)
        if self.save:
            with open("goodreads-search.html", "w") as fp:
                fp.write(response.text)

        books = []
        for elm in doc.xpath('//tr[@itemtype="http://schema.org/Book"]'):
            book = Book(elm)
            book.match(self.query)
            books.append(book)

        books = sorted(books, key=lambda b: b.score, reverse=True)
        threshold = 1
        matches = None
        while not matches:
            matches = [b for b in books if b.score >= threshold]
            if threshold <= 0:
                break
            threshold -= 0.15

        books = matches
        return books
