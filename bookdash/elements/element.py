"""A module for parsing data from HTML elements."""

import lxml.html as parser
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
        if isinstance(element, str):
            element = parser.fromstring(element)
        self.element = element

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
