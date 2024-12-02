import lxml.html
import pytest

from bookdash.elements.book_page_element import BookPageElement


@pytest.mark.parametrize("filecontents",
                         [{'filename': "goodreads-book-15784263.html"}],
                         indirect=True)
def test_title(filecontents):
    book = BookPageElement(filecontents)
    assert book.id == 15784263
    assert book.title == "Dead Things"
    assert book.author == "Stephen Blackmoore"
    assert book.series == "Eric Carter"
    assert book.number == 1


@pytest.mark.parametrize("filecontents",
                         [{'filename': "goodreads-book-15784263.html"}],
                         indirect=True)
def test_no_rating(filecontents):
    book = BookPageElement(filecontents)
    assert not book.rating


@pytest.mark.parametrize("filecontents",
                         [{'filename': "goodreads-book-5776788.html"}],
                         indirect=True)
def test_with_rating(filecontents):
    ...
