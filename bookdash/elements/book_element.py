"""A module for parsing data from HTML elements."""

import re

from more_itertools import padded

from .element import Element

__all__ = ["Element"]


class BookElement(Element):
    """A class for parsing a book tr from Goodreads search results."""

    TITLE_PARSER_FULL = re.compile(
        r'^(?P<name>.*) \((?P<series>.*) #(?P<number>.*)\)$'
    )
    TITLE_PARSER = re.compile(r'^(?P<name>.*) \((?P<series>.*)\)$')

    def __init__(self, element=None):
        """Parse book attributes from element."""
        super().__init__(element)
        self._series = None
        self.number = None
        if self.element is None:
            return

        self.id = self.attr('.//div[@class="u-anchorTarget"]', "id")
        self.author = self.first(
            './/span[@itemprop="author"]//span[@itemprop="name"]/text()'
        )
        self.title = self.first('.//a[@class="bookTitle"]/span/text()')

    @property
    def title(self):
        """Title getter."""
        return self._title

    @title.setter
    def title(self, value):
        """Title setter that parses any series and number from title."""
        if "(" in value:
            match = self.TITLE_PARSER_FULL.search(value)
            if not match:
                match = self.TITLE_PARSER.search(value)
            if not match:
                print(f"match not found for: {value}")
                return

            value, self.series, self.number = padded(match.groups(), None, 3)

        self._title = value

    @property
    def series(self):
        """Series getter."""
        return self._series

    @series.setter
    def series(self, value):
        """Series setter that removes trailing comma."""
        if value.endswith(","):
            value = value[0:-1]

        self._series = value
