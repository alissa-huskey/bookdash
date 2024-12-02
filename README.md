bookdash
========

> a personal CLI util to summarize book info

tl;dr
-----

```
dash "Ender's Game"
```

Usage
-----

```
Usage: dash [<filters>] [<title>]

  Search for book and print details.

Options:
  -t, --title TEXT        filter by book title
  -a, --author TEXT       filter by book author
  -s, --series TEXT       filter by book series
  -S, --save / --no-save  save requested contents for debugging
  --help                  Show this message and exit.
```

### Setup

Copy `bookdash/private.py` to `bookdash/_private.py` and edit with your login info.
