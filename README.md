bookdash
========

> A dashboard for books.

This is a personal CLI util to summarize book info. Eventually I hope to
summarize information across several services. For now, it's just goodreads.

tl;dr
-----

```
books "Ender's Game"
```

Usage
-----

```
Usage: books [<filters>] [<title>]

  Search for book and print details.

Options:
  -c, --init-config       initialize config file and print path
  -t, --title TEXT        filter by book title
  -a, --author TEXT       filter by book author
  -s, --series TEXT       filter by book series
  -S, --save / --no-save  save requested contents for debugging
  --help                  Show this message and exit.
```

Config
------

The bookdash config file is typically stored at
`~/.config/bookdash/bookdash.toml`. (Though this may vary depending on your
system and environment variables.)

To follow are all of the configuration settings available. Environment
variables supersede any settings in the config file. More specific
settings supersede more general settings.

| Conf File Name  | Environment Variable   | Description                   | Default                                   |
|-----------------|------------------------|-------------------------------|-------------------------------------------|
|                 | `BOOKDASH_CONFIG_FILE` | Path to bookdash config file. | `$XDG_CONFIG_HOME/bookdash/bookdash.toml` |
|                 | `BOOKDASH_CONFIG_DIR`  | `bookdash.toml` directory.    | `$XDG_CONFIG_HOME/bookdash/`              |
| data_dir        | `BOOKDASH_DATA_DIR`    | Bookdash user data directory. | `$XDG_DATA_HOME/bookdash/`                |
|                 | `XDG_CONFIG_HOME`      | User config directory.        | `$HOME/.config`                           |
|                 | `XDG_DATA_HOME`        | User data directory.          | `$HOME/.local/share`                      |
| goodreads_email | `GOODREADS_EMAIL`      | Your goodreads email address. |                                           |
| goodreads_pwd   | `GOODREADS_PWD`        | Your goodreads password.      |                                           |

See also [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/).

Status
------

**Pre-Alpha**

In development. Works for me, but quirky and unreliable.
