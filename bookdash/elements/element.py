"""A module for parsing data from HTML elements."""

import lxml.html as parser
from bs4 import BeautifulSoup
from lxml import etree
from lxml.etree import ParseError
from more_itertools import first

__all__ = ["Element"]


class Element:
    """Element class providing shorthand methods for lxml objects."""

    def __init__(self, element=None):
        """Set lxml element.

        Params
        ------
        element (str, parser.HtmlElement): Element or string to generate one
        """
        if element is None:
            self.raw = ""
            self.element = None
            return

        if isinstance(element, str):
            self.raw = element
            try:
                element = parser.fromstring(element)
            except (BaseException, ParseError):
                element = None
        else:
            self.raw = etree.tostring(element)

        self.element = element

    @property
    def doc(self):
        """Return a BeautifulSoup document."""
        return BeautifulSoup(self.raw, "html.parser")

    def xpath(self, path) -> list:
        """Return the list of objects for path.

        Params
        ------
        path (str): xpath
        """
        return self.element.xpath(path)

    def first(self, path) -> object:
        """Return the first object for path or None.

        Params
        ------
        path (str): xpath
        """
        return first(self.xpath(path), None)

    def attr(self, path, name) -> object:
        """Return the attr for name of the first object for path or None.

        Params
        ------
        path (str): xpath
        name (str): attribute name
        """
        elm = self.first(path)
        if elm is None:
            return
        return elm.attrib.get("id")
