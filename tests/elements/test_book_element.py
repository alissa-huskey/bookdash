import lxml.html
import pytest

from bookdash.elements.book_element import BookElement


def test_title_setter_plain():
    book = BookElement()
    book.title = "Dead Things"

    assert book.title == "Dead Things"
    assert not book.series
    assert not book.number
    assert not book.author


def test_title_setter_with_series():
    book = BookElement()
    book.title = "Dead Things (Eric Carter)"

    assert book.title == "Dead Things"
    assert book.series == "Eric Carter"
    assert not book.number
    assert not book.author


def test_title_setter_with_series_number():
    book = BookElement()
    book.title = "Dead Things (Eric Carter, #1)"

    assert book.title == "Dead Things"
    assert book.series == "Eric Carter"
    assert book.number == 1
    assert not book.author


def test_title_setter_full():
    book = BookElement()
    book.title = "Dead Things (Eric Carter, #1) by Stephen Blackmoore"

    assert book.title == "Dead Things"
    assert book.author == "Stephen Blackmoore"
    assert book.series == "Eric Carter"
    assert book.number == 1
