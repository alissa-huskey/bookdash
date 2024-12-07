"""Module for the command line interface."""

import click
from click import confirm, prompt
from rich import print as rprint
from tabulate import tabulate
from xdg.BaseDirectory import save_config_path

from bookdash import abort, error, log
from bookdash.clients.goodreads_client import GoodreadsClient
from bookdash.config import Config, GoodreadsConfig, init_config

bp = breakpoint


def trim(text, width) -> str:
    """Return text trimmed to width."""
    if not text:
        return ""
    text = str(text)
    if len(text) <= width:
        return text

    return f"{text[0:width-3]}..."

def config_init():
    """Print the path to the config file then initialize file."""
    config = Config()
    file = config.config_file

    print(f"Config file path: {file}")

    if not file.is_file():
        go_ahead = confirm("Initialize file?")
        if not go_ahead:
            return

        #  file.mkdir(parents=True, exist_ok=True)
        init_config(file)


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
