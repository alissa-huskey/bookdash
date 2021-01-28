"""A module for parsing data from HTML elements"""

import lxml.html as parser
from more_itertools import first, padded
import re

__all__ = ["BookElement", "Element"]

class Element:
    """Element class providing shorthand methods for lxml objects"""

    TITLE_PARSER_FULL = re.compile('^(?P<name>.*) \((?P<series>.*) #(?P<number>.*)\)$')
    TITLE_PARSER = re.compile('^(?P<name>.*) \((?P<series>.*)$')

    def __init__(self, element):
        """Set lxml element

            Params
            ------
            element (str, lxml.html.HtmlElement): element object or string to generate one
        """
        if isinstance(element, str):
            element = parser.fromstring(element)
        self.element = element

    def xpath(self, path) -> list:
        """Return the list of objects for path

            Params
            ------
            path (str): xpath
        """
        return self.element.xpath(path)

    def first(self, path) -> object:
        """Return the first object for path or None

            Params
            ------
            path (str): xpath
        """
        return first(self.xpath(path), None)

    def attr(self, path, name) -> object:
        """Return the attr for name of the first object for path or None

            Params
            ------
            path (str): xpath
            name (str): attribute name
        """
        elm = self.first(path)
        if elm is not None:
            return
        return elm.attrib.get("id")

class BookElement(Element):
    """A class for parsing a book tr from Goodreads search results"""

    def __init__(self, element):
        """Parse book attributes from element"""
        super().__init__(element)
        self.id = self.attr('.//div[@class="u-anchorTarget"]', "id")
        self.author = self.first('.//span[@itemprop="author"]//span[@itemprop="name"]/text()')
        self.title = self.first('.//a[@class="bookTitle"]/span/text()')

    @property
    def title(self):
        """title getter"""
        return self._title

    @title.setter
    def title(self, value):
        """Title setter that parses any series and number from title"""

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
        """Series getter"""
        return self._series

    @series.setter
    def series(self, value):
        """Series setter that removes trailing comma"""
        if value.endswith(","):
            value = value[0:-1]

        self._series = value
