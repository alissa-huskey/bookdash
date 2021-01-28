import pytest

from . import Stub
from bookdash.books import Book
from bookdash.elements import BookElement


def test_init():
    book = Book(Stub(klass=BookElement, title="Vicious", author="V.E. Schwab"))
    assert book.title == "Vicious"
    assert book.author == "V.E. Schwab"


def test_url():
    book = Book()
    book.id = "19089701"
    assert book.url == "https://www.goodreads.com/book/show/19089701"


def test_match():
    book = Book()
    book.title = "City of Ghosts"
    book.match({'title': "city of ghosts"})
    assert book.score == 1
    assert len(book.matches) == 1
