"""Module for the command line interface."""

from typing import Collection

import click
from click import confirm, prompt
from html2text import HTML2Text
from rich import box
from rich import print as rprint
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.traceback import install as rich_tracebacks
from sqlmodel import select
from tabulate import tabulate
from xdg.BaseDirectory import save_config_path

from bookdash import abort, error, log
from bookdash.clients.goodreads_client import GoodreadsClient
from bookdash.config import Config, GoodreadsConfig, init_config
from bookdash.db import DB
from bookdash.models.goodreads_book import GoodreadsBook

bp = breakpoint

rich_tracebacks(show_locals=True)

console = Console()


def titlize(text: str) -> str:
    """Convert text to title.

    Example:
        >>> titlize("my_project")
        'My Project'
    """
    return text.replace("_", " ").title()


def mktable(title: str) -> Table:
    """Return a rich Table intended for left-header display titled `title`."""
    table = Table(
        #  title=title,
        show_header=False,
        show_lines=True,
        pad_edge=True,
        expand=True,
        title_style="magenta bold",
        style="magenta",
    )
    table.add_column()
    table.add_column()
    return table


def style(text: str, style: str) -> str:
    """Return rich styled text.

    Args:
        text (srt): text to style
        style (str): rich style string
    """
    t = Text(text)
    t.stylize(style),
    return t


def trim(text: str, width: int) -> str:
    """Return text trimmed to width.

    Example:
        >>> text = 'Lorem ipsum odor amet, consectetuer adipiscing elit.'
        >>> trim(text, 30)
        'Lorem ipsum odor amet, cons...'
    """
    if not text:
        return ""
    text = str(text)
    if len(text) <= width:
        return text

    return f"{text[0:width-3]}..."


# TODO: this should be a command
#       right now it's being called from search() if --init-config is passed
def config_init():
    """Print the path to the config file then initialize file."""
    config = Config()
    file = config.config_file

    print(f"Config file path: {file}")

    if not file.is_file():
        go_ahead = confirm("Initialize file?")
        if not go_ahead:
            return

        init_config(file)


def get_keys(data: dict, fields: Collection, keep_empty: bool=False) -> dict:
    """Return a new dict containing the items with keys matching fields.

    Args:
        data (dict): the source dictionary
        fields (Collection): the fields to include
        keep_empty (bool, default=False): exclude items with empty values

    Example:
        >>> data = dict(zip("abcde", range(1, 6)))
        >>> get_keys(data, ("a", "c", "e"))
        {'a': 1, 'c': 3, 'e': 5}
    """

    new = {
        k: data[k] for k in fields
        if k in data and (keep_empty or data.get(k))
    }
    return new

@click.command(context_settings={"ignore_unknown_options": True},
               options_metavar="[<filters>]")
@click.option("-c", "--init-config", is_flag=True, help="initialize config file and print path")
@click.option("-t", "--title", help="filter by book title")
@click.option("-a", "--author", help="filter by book author")
@click.option("-s", "--series", help="filter by book series")
@click.option('--save/--no-save', '-S/', default=False,
              help="save requested contents for debugging")
@click.argument("query", nargs=-1, metavar="[<title>]")
def search(**kwargs):
    """Search for book and print details."""
    log(prefix="cli.search() kwargs:", **kwargs)

    init = kwargs.pop("init_config")
    if init:
        config_init()
        return

    if kwargs["query"]:
        kwargs["title"] = " ".join(kwargs.pop("query"))

    if not any(kwargs.values()):
        abort("Received no search arguments.")

    creds = GoodreadsConfig()
    api = GoodreadsClient(**kwargs)
    #  api.login(creds.email, creds.pwd)
    books = api.search()
    rows = []
    for i, book in enumerate(books, 1):
        rows.append({
            '#': i,
            'Title': trim(book.title, 60),
            'Author': book.author,
            'Series': trim(book.series, 40),
        })

    if not rows:
        return

    print()
    print(tabulate(rows, headers="keys"))

    if not books:
        return

    # prompt user to enter book number
    if len(books) == 1:
        book = books[0]
    else:
        book = None
        while book is None:
            reply = prompt("Book # >").strip()
            if reply.lower() == "q":
                return

            try:
                book_no = int(reply) - 1

                if book_no < 0:
                    raise ValueError()
                book = books[book_no]

            except (ValueError, IndexError):
                print()
                error(f"Invaid response. Please enter 1-{len(books)}")
                continue
    show(book)

def show(book):
    """Show book details."""

    # fields to display in the book info table
    book_info_fields = (
        "title",
        "author",
        "series",
        "additional_authors",
        "isbn",
        "isbn13",
        "year_published",
        "original_year_published",
        "publisher"
        "binding",
        "pages",
        "year_published",
        "original_year_published",
    )

    # fields to display in my goodreads info table
    my_info_fields = (
        "id",
        "average_rating",
        "date_added",
        "read_count",
        "date_read",
        "bookshelves",
        "bookshelves_with_positions",
        "exclusive_shelf",
        "my_rating",
        "owned_copies",
        "read_count",
    )

    # fields to display long form
    my_info_long_fields = (
        "private_notes",
        "my_review",
    )


    db = DB()
    row = db.select_one(GoodreadsBook, GoodreadsBook.id == int(book.id))

    book_data = book.to_dict().copy()
    book_data.update(row)

    book_table = mktable("Book")

    for name, value in get_keys(book_data, book_info_fields).items():
        book_table.add_row(
            style(titlize(name), "bold cyan"),
            str(value),
        )

    gr_table = mktable("Goodreads User Info")
    for name, value in get_keys(book_data, my_info_fields).items():
        gr_table.add_row(
            style(titlize(name), "bold cyan"),
            str(value),
        )

    longform_panels = []
    for name, value in get_keys(book_data, my_info_long_fields).items():
        parser = HTML2Text(bodywidth=console.width-5)
        text = parser.handle(book_data.get(name)).strip()
        height = len(text.splitlines())

        panel = Panel(
            text,
            title=style(titlize(name), "magenta"),
            border_style="blue",
            height=height,
        )
        layout = Layout(panel)
        longform_panels.append(panel)

    #  parser = HTML2Text(bodywidth=console.width-5)
    #  private_notes = parser.handle(book_data.get("private_notes")).strip()

    layout = Layout()

    layout.split_column(
        Layout(size=1),
        Layout(name="upper"),
        *longform_panels,
    )

    layout["upper"].split_row(
        Panel(book_table, title=style("Book Details", "magenta"), border_style="blue"),
        Panel(gr_table, title=style("Goodreads Details", "magenta"), border_style="blue"),
    )

    rprint(layout)
