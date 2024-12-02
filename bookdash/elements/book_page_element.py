"""A module for parsing book data from the a Goodreads search results row."""

import re
from functools import cached_property

from more_itertools import first

from .book_element import BookElement

__all__ = ["BookPageElement"]


class BookPageElement(BookElement):
    """A class for parsing book data from Goodreads book page."""

    ID_MATCHER = re.compile(r"(?P<id>\d+)[^/]*$")

    def __init__(self, element=None):
        """Parse book attributes from element."""
        super().__init__(element)
        self.title = self.doc.title.text.removesuffix(" | Goodreads")

    @cached_property
    def id(self):
        """Return the book id, parsed from the canonical link href."""
        link = first(self.doc.find_all("link", rel="canonical"))
        if not link:
            return

        href = link.attrs.get("href", "")
        res = self.ID_MATCHER.search(href)
        if not res:
            return

        return int(res.group("id"))

    @cached_property
    def rating(self):
        """Return the rating parsed from the page."""

