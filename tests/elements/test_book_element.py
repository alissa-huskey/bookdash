import lxml.html
import pytest

from bookdash.elements.book_element import BookElement

from .. import filecontents


@pytest.mark.parametrize("filecontents",
                         [{'filename': "goodreads-search-book.html"}],
                         indirect=True)
def test_book_parsing(filecontents):
    book = BookElement(filecontents)
    assert book.title == "Ender's Game"
    assert book.author == "Orson Scott Card"
    assert book.series == "Ender's Saga"
    assert book.number == "1"


def test_book_title():
    book = BookElement()
    book.title = "The End Game"
    assert book.title == "The End Game"
    assert not book.series
    assert not book.number


def test_book_title_with_series():
    book = BookElement()
    book.title = "Ender's Game, Volume 1: Battle School (Ender's Saga)"
    assert book.title == "Ender's Game, Volume 1: Battle School"
    assert book.series == "Ender's Saga"
    assert not book.number


def test_book_title_with_series_and_num():
    book = BookElement()
    book.title = "The End Game (Love Games #2)"
    assert book.title == "The End Game"
    assert book.series == "Love Games"
    assert book.number == "2"


def test_book_title_with_series_and_num_and_comma():
    book = BookElement()
    book.title = "Ender's Game (Ender's Saga, #1)"
    assert book.title == "Ender's Game"
    assert book.series == "Ender's Saga"
    assert book.number == "1"


def test_book_series():
    book = BookElement()
    book.series = "Ender's Saga"
    # book.series = "Ender's Saga, #1"
    assert book.series == "Ender's Saga"


def test_book_series_with_trailing_comma():
    book = BookElement()
    book.series = "Ender's Saga,"
    assert book.series == "Ender's Saga"