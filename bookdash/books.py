"""Module for Book objects"""

from difflib import SequenceMatcher
import re

from .elements import BookElement


__all__ = ["Book"]


class Book:
    """Goodreads Books"""

    ATTRS = {
        'id': None,
        'title': "property",
        'author': None,
        'series': "property",
        'number': None,
        'score': None,
    }

    def __init__(self, element=None):
        """Initialize book attributes."""
        for attr, prop in self.ATTRS.items():
            if prop: attr = f"_{attr}"
            setattr(self, attr, None)
        self.element = element

    def __repr__(self):
        return f"Book({self.title!r})"

    @property
    def url(self) -> str:
        """Return the goodreads book url"""
        return f"https://www.goodreads.com/book/show/{self.id}"

    @property
    def element(self):
        """."""
        return self._element

    @element.setter
    def element(self, book):
        """."""
        if book is None:
            return
        if not isinstance(book, BookElement):
            book = BookElement(book)
        for attr in self.ATTRS:
            setattr(self, attr, getattr(book, attr, None))

    def match(self, params: dict):
        """Calculate a match score based on params"""
        self.matches = {}
        filterer = re.compile(r"(?!\w|\s).")

        if params.get("query"):
            self.score = 0
            return

        if "query" in params:
            params.pop("query")

        simplify = lambda text: filterer.sub("", str(text).lower().strip())

        for name, want in params.items():
            if not want:
                continue
            have = getattr(self, name)
            ratio = SequenceMatcher(None, simplify(have), simplify(want)).ratio()
            self.matches[name] = ratio

        self.score = sum(self.matches.values()) / len(self.matches.values())
