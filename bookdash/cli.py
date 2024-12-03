"""Module for the command line interface."""

import click
from click import prompt
from rich import print as rprint
from tabulate import tabulate

from . import abort, clients, error, log

bp = breakpoint


def trim(text, width) -> str:
    """Return text trimmed to width."""
    if not text:
        return ""
    text = str(text)
    if len(text) <= width:
        return text

    return f"{text[0:width-3]}..."


@click.command(context_settings={"ignore_unknown_options": True},
               options_metavar="[<filters>]")
@click.option("-t", "--title", help="filter by book title")
@click.option("-a", "--author", help="filter by book author")
@click.option("-s", "--series", help="filter by book series")
@click.option('--save/--no-save', '-S/', default=False,
              help="save requested contents for debugging")
@click.argument("query", nargs=-1, metavar="[<title>]")
def search(**kwargs):
    """Search for book and print details."""
    log(prefix="cli.search() kwargs:", **kwargs)

    if kwargs["query"]:
        kwargs["title"] = " ".join(kwargs.pop("query"))

    if not any(kwargs.values()):
        abort("Received no search arguments.")

    api = clients.Client(**kwargs)
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

    row = None

    if len(rows) == 1:
        row = rows [0]

    while not row:
        response = prompt("Book #> ", type=int)

        try:
            row = rows[response-1]
        except IndexError:
            error("Invalid book number. Try again.")

    show(row.id)


def show(url):
    """Show book details."""

    rprint(row)
