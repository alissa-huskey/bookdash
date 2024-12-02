"""A module for parsing book data from a Goodreads element."""

import re

from .element import Element

__all__ = ["BookElement"]


class BookElement(Element):
    """A class for parsing book data any Goodreads markup."""

    # 'Dead Things (Eric Carter, #1)'
    # 'Dead Things (Eric Carter, #1) by Stephen Blackmoore'
    TITLE_PARSER_FULL = re.compile(
        r'^(?P<title>.*) '
        r'\((?P<series>.*) #(?P<number>.*)\)'
        r'( by (?P<author>.*))?$'
    )

    # 'Dead Things (Eric Carter, #1)'
    TITLE_PARSER = re.compile(r'^(?P<title>.*) \((?P<series>.*)\)$')
    DEFAULT_TITLE_VALUES = {
        k: None for k in ["series", "number", "author"]
    }

    def __init__(self, element=None):
        """Parse book attributes from element."""
        super().__init__(element)
        self._title = None
        self._series = None
        self.number = None

    @property
    def title(self):
        """Title getter."""
        return self._title

    @title.setter
    def title(self, value):
        """Title setter that parses any series and number from title."""
        self._title = value
        matches = self.DEFAULT_TITLE_VALUES.copy()

        if "(" in value:
            if not (match := self.TITLE_PARSER_FULL.search(value)):
                match = self.TITLE_PARSER.search(value)

            if not match:
                print(f"match not found for: {value}")
                return

            matches.update(match.groupdict())

            self._title = matches.pop("title")

        for attr, value in matches.items():
            if not hasattr(self, attr):
                setattr(self, attr, None)
            if value:
                setattr(self, attr, value)

        if self.number and self.number.isnumeric():
            self.number = int(self.number)

    @property
    def series(self):
        """Series getter."""
        return self._series

    @series.setter
    def series(self, value):
        """Series setter that removes trailing comma."""
        if not value:
            return

        if value.endswith(","):
            value = value[0:-1]

        self._series = value
