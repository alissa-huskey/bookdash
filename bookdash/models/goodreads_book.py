"""Goodreads Books from "My Books" CSV export."""

from datetime import date, datetime
from typing import Annotated, Optional, Callable, TypeVar
from functools import reduce

from pydantic import field_validator
from sqlmodel import Field, Session, SQLModel, create_engine, select

bp = breakpoint

T = TypeVar("T")


MAPPING = {
    "Book Id": "id",
    "Number of Pages": "pages",
    "Original Publication Year": "original_year_published",
    "Author l-f": "author_last_first",
}
"""CSV heading field names -> GoodreadsBook attribute name."""

def none_if_blank(value: T) -> Optional[T]:
    """Return None if value is falsy."""
    return value or None

def str_to_bool(value: str) -> bool:
    """Return None if value is falsy."""
    return value.lower() == "true"

def str_to_int(value: T) -> Optional[T]:
    """Cast numeric str to int."""
    try:
        return int(value)
    except ValueError:
        return None

def str_to_float(value: T) -> Optional[T]:
    """Cast numeric str to float."""
    return float(value)

def fix_isbn(value: str) -> Optional[str]:
    """Remove the ="" from the ISBN numbers."""
    number = value.lstrip('="').rstrip('"')
    return number or None

def str_to_date(value: str) -> date:
    """Return date() object from str format "YYYY/MM/DD"."""
    return datetime.strptime("2024/12/06", "%Y/%m/%d").date()

TRANSFORMERS = {
    "*": (none_if_blank,),
    "id": (str_to_int,),
    "year_published": (str_to_int,),
    "original_year_published": (str_to_int,),
    "isbn": (fix_isbn,),
    "isbn13": (fix_isbn,),
    "date_read": (str_to_date,),
    "date_added": (str_to_date,),
    "spoiler": (str_to_bool,),
}
"""Transformer functions to run on fields."""

def head_to_attr(heading: str) -> str:
    """Convert CSV heading name to model attribute name.

    Return name from MAPPING if it exists.
    Otherwise return the lowercased, underscored version of heading.
    """
    if (name := MAPPING.get(heading)):
        return name
    name = heading.lower().replace(" ", "_")
    return name

def field_callbacks(heading: str) -> tuple[Callable]:
    """Return a tuple of transformer callbacks for a given field."""
    attr = head_to_attr(heading)
    field_functs = TRANSFORMERS.get(attr, tuple())
    global_functs = TRANSFORMERS.get("*", tuple())
    return field_functs + global_functs


def from_csv(csv_data) -> SQLModel:
    """Create GoodreadsBook instance from CSV row."""
    attrs = {
        # key: new heading name
        # value: the value returned from all transform callbacks
        head_to_attr(heading): reduce(
            # calls each successive transform function on the previously
            # returned value
            lambda v, func: func(v),
            # list of callbacks for this field
            field_callbacks(heading),
            # the inital value
            value
        )
        for heading, value in csv_data.items()
    }
    inst = GoodreadsBook(**attrs)
    return inst


class GoodreadsBook(SQLModel, table=True):
    """Database table model for a goodreads book."""

    id: int = Field(primary_key=True)
    title: str = Field(index=True)
    author: str = Field(index=True)
    author_last_first: str
    additional_authors: Optional[str]
    average_rating: Optional[float]
    my_rating: Optional[int]
    publisher: Optional[str]
    binding: Optional[str]
    pages: Optional[int]
    year_published: Optional[int]
    original_year_published: Optional[int]
    isbn: Optional[str] = Field(index=True)
    isbn13: Optional[str] = Field(index=True)
    my_rating: Optional[int]
    date_read: Optional[date]
    date_added: Optional[date]
    bookshelves: Optional[str]
    bookshelves_with_positions: Optional[str]
    exclusive_shelf: Optional[str]
    my_review: Optional[str]
    spoiler: Optional[bool] = Field(default=False)
    private_notes: Optional[str]
    read_count: Optional[int]
    owned_copies: Optional[int]
