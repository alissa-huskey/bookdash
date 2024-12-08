"""Messing around with SQLModel."""

from random import choices

from rich.traceback import install as rich_tracebacks
from sqlmodel import Field, Session, SQLModel, create_engine, select, or_

from bookdash.config import Config, ConfigFile
from bookdash.csv_file import CsvFile
from bookdash.db import DB
from bookdash.models.goodreads_book import GoodreadsBook, from_csv

bp = breakpoint

rich_tracebacks(show_locals=True)


def import_from_csv():
    """Import GoodreadsBook objects from a exported Goodreads CSV file."""

    gr_books = CsvFile("tmp/2024-12-06-goodreads.csv")
    gr_books.read()

    #  books = [from_csv(data) for data in choices(gr_books, k=5)]
    books = [from_csv(data) for data in gr_books]

    db = DB()
    db.create()

    with db.session as session:
        for book in books:
            session.add(book)

        session.commit()

        # must access books here,
        # AFTER commit but BEFORE session is closed,
        # to have valid book objects
        [x.id for x in books]

        print("session committed.")

    print("session closed.")
    bp()

    print("goodbye")


def select_books():
    """Demo quering a database table using SQLModel."""
    # this is an example of a complete book that is (currently) in the db
    warrior = Book(
        id=15,
        title='Warrior King (Odyssey One, #5)',
        author='Evan Currie',
        publisher='47North',
        binding='Kindle Edition',
        pages=334,
        year_published=2016,
        original_year_published=2016,
        isbn='="1503990974"',
        isbn13='="9781503990975"',
    )

    db = DB()

    book = Book(
        title='Warrior King (Odyssey One, #5)',
        author='Evan Currie',
    )

    with db.session as session:
        # WHERE clause
        query = select(Book).where(Book.title == warrior.title)
        results = session.exec(query)
        row = results.one_or_none()
        # NOTE: after this, the results object is closed and can't be used
        # again

        # multiple WHERE clauses
        query = select(Book).where(Book.id >= 10, Book.id <= 12)
        results = session.exec(query)
        rows = results.all()

        # multiple WHERE clauses, another way
        query = select(Book).where(Book.year_published >= 2020).where(Book.year_published < 2021)
        results = session.exec(query)
        rows = results.all()

        # multiple WHERE clauses with OR
        query = select(Book).where(or_(
            Book.binding == "Kindle Edition",
            Book.binding == "ebook"
        ))
        results = session.exec(query)
        rows = results.all()

        # select by ID shortcut
        book = session.get(Book, 15)


if __name__ == "__main__":
    import_from_csv()
