"""A module for parsing book data from the a Goodreads search results row."""

from .book_element import BookElement

bp = breakpoint

__all__ = ["FoundBookElement"]


class FoundBookElement(BookElement):
    """A class for parsing a book TR from Goodreads search results."""

    def __init__(self, element=None):
        """Parse book attributes from element."""
        super().__init__(element)
        if self.element is None:
            return

        self.id = self.attr('.//div[@class="u-anchorTarget"]', "id")
        self.author = self.first('.//a[@class="authorName"]/span/text()')
        self.title = self.first('.//a[@class="bookTitle"]/span/text()')
        self.url = self.first('.//a[@class="bookTitle"]/@href')
