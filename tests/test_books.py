from bookdash.books import Book
from bookdash.elements.book_element import BookElement

from . import Stub


def test_init():
    book = Book(Stub(klass=BookElement, title="Vicious", author="V.E. Schwab"))
    assert book.title == "Vicious"
    assert book.author == "V.E. Schwab"


def test_url():
    book_id = "19089701"
    book = Book(id=book_id)
    assert book.url == f"https://www.goodreads.com/book/show/{book_id}"


def test_element_setter():
    element = Stub(klass=BookElement, title="Vicious", author="V.E. Schwab")
    book = Book(element)

    assert book.element == element


def test_element_getter():
    element = Stub(klass=BookElement, title="Vicious", author="V.E. Schwab")
    book = Book()
    book._element = element

    assert book.element == element


def test_element_getter():
    element = Stub(klass=BookElement, title="Vicious", author="V.E. Schwab")
    book = Book(element)

    assert book.element == element


def test_match():
    book = Book()
    book.title = "City of Ghosts"
    book.match({'title': "city of ghosts"})
    assert book.score == 1
    assert len(book.matches) == 1
