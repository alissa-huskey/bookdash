"""Goodreads client module."""

from functools import partialmethod

import requests
from bs4 import BeautifulSoup
from more_itertools import first

from bookdash import abort, log
from bookdash.books import Book
from bookdash.elements.element import Element
from bookdash.clients.base_client import BaseClient

bp = breakpoint

__all__ = ["GoodreadsClient"]


class GoodreadsClient(BaseClient):
    """Goodreads client."""

    def __init__(self, **kwargs):
        """Goodreads client.

        Params
        ------
        title (str): title to filter by
        author (str): author to filter by
        series (str): series to filter by
        query (str): submit query and return all results
        save (bool): save response content for debugging
        """
        self.save = kwargs.pop("save", False)

        search_fields = ("query", "title", "author", "series")
        self.query = {
            key: val for key,val in kwargs.items()
            if val and key in search_fields
        }
        for attr in search_fields:
            kwargs.pop(attr, None)

        self.search_by = "all"

        attrs = self.query.keys()
        if len(attrs) == 1 and first(attrs) in ["title", "author"]:
            self.search_by = first(attrs)

        super().__init__(**kwargs)

    def login(self, email, password):
        """Login to goodreads."""

    def search(self) -> list:
        """Submit a query to goodreads and return a list of Book objects.

        Examples
        --------
        >>> api = GoodreadsClient(title="ender's game", author="orson scott card")
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

    def show(self):
        """Submit a request to show a book by ID and return the details for
        that book."""
