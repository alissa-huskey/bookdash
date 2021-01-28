"""Module for web scraping clients that can be operated like API clients."""

from functools import partialmethod
from os import _exit as exit
import urllib.parse as url

from more_itertools import first
import requests

from . import abort, log
from .books import Book
from .elements import Element
from .private import GOODREADS_EMAIL, GOODREADS_PWD


class Client:
    """Goodreads client"""
    AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'

    def __init__(self):
        """Create session"""
        self.session = requests.session()
        self.session.headers.update({'user-agent': self.AGENT})

    def request(self, method, url, **kwargs):
        """Make a session request"""
        resp = self.session.request(method, url)
        if not resp.ok:
            abort(f"Request to {url} failed:", "\n", resp.status_code, resp.reason)
        return resp
    get = partialmethod(request, "GET")
    post = partialmethod(request, "POST")
    options = partialmethod(request, "OPTIONS")
    head = partialmethod(request, "HEAD")
    put = partialmethod(request, "PUT")
    patch = partialmethod(request, "PATCH")
    delete = partialmethod(request, "DELETE")

    def login(self):
        """login to goodreads"""
        resp = self.get("https://www.goodreads.com/user/sign_in")
        doc = parser.fromstring(resp.text)
        form = doc.first('//*[@id="emailForm"]/form/fieldset')

        if not form:
            abort("Login form not found")

        data = {field.name:field.value for field in form.xpath(f'//input')
                if not field.name.startswith("user")}
        data.update({
            'user[email]': GOODREADS_EMAIL,
            'user[password]': GOODREADS_PWD,
        })

        resp = self.session.post(
            "https://www.goodreads.com/user/sign_in",
             data=data,
        )

    def search(self, **kwargs) -> list:
        """Submit a query to goodreads and return a list of Book objects.

        Params
        ------
        title (str): title to filter by
        author (str): author to filter by
        series (str): series to filter by
        query (str): submit query and return all results
        save (bool): save response content for debugging

        Examples
        --------
        >>> search(title="ender's game", "author"="orson scott card")
        [Book("Ender's Game")]
        """
        save = kwargs.pop("save", False)
        search_by = "all"
        kwargs = {key: val for key, val in kwargs.items()
                  if val and key in ("query", "title", "author", "series")}

        if len(kwargs.keys()) == 1 and first(kwargs.keys()) in ["title", "author"]:
            search_by = first(kwargs.keys())

        query = url.quote(" ".join(kwargs.values()))
        resp = self.get(f"https://www.goodreads.com/search?q={query}",
                        params={'search[field]': search_by})
        log(prefix="Client.search() query:", query=query, search_by=search_by)

        doc = Element(resp.text)
        if save:
            with open("goodreads-search.html", "w") as fp:
                fp.write(resp.text)

        books = []
        for elm in doc.xpath('//tr[@itemtype="http://schema.org/Book"]'):
            book = Book(elm)
            book.match(kwargs)
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
