"""Module for Book objects."""

import re
from difflib import SequenceMatcher

from .elements import BookElement

__all__ = ["Book"]


class Book:
    """Goodreads Books."""

    ATTRS = {
        'id': None,
        'title': "property",
        'author': None,
        'series': "property",
        'number': None,
        'score': None,
    }

    MATCH_FILTERER = re.compile(r"(?!\w|\s).")

    def __init__(self, element=None):
        """Initialize book attributes."""
        for attr, prop in self.ATTRS.items():
            if prop:
                attr = f"_{attr}"
            setattr(self, attr, None)
        self.element = element

    def __repr__(self):
        """Book class repr."""
        return f"Book({self.title!r})"

    @property
    def url(self) -> str:
        """Return the goodreads book url."""
        return f"https://www.goodreads.com/book/show/{self.id}"

    @property
    def element(self):
        """Element getter."""
        return self._element

    @element.setter
    def element(self, book):
        """Element setter."""
        if book is None:
            return
        if not isinstance(book, BookElement):
            book = BookElement(book)
        for attr in self.ATTRS:
            setattr(self, attr, getattr(book, attr, None))

    def normalize(self, text):
        """Normalize text for search."""
        return self.MATCH_FILTERER.sub("", str(text).lower().strip())

    def match(self, params: dict):
        """Calculate a match score based on params."""
        self.matches = {}

        if params.get("query"):
            self.score = 0
            return

        if "query" in params:
            params.pop("query")

        for name, want in params.items():
            if not want:
                continue
            have = getattr(self, name)
            ratio = SequenceMatcher(
                None,
                self.normalize(have),
                self.normalize(want)
            ).ratio()
            self.matches[name] = ratio

        self.score = sum(self.matches.values()) / len(self.matches.values())
