"""."""

import logging
from functools import partialmethod
from os import environ
from sys import exit, stderr

from click import style

__all__ = ["__version__", "abort", "log"]

__version__ = "0.1.0"


def error(*args):
    """Print message to stderr."""
    print(style("Error", fg="red"), *args, file=stderr)
    exit(1)


def abort(*args):
    """Print message to stderr and exit."""
    error(*args)
    exit(1)


class forward_attr(object):
    """
    A descriptor based recipe that makes it possible to write shorthands
    that forward attribute access from one object onto another.

    >>> class C(object):
    ...     def __init__(self):
    ...         class CC(object):
    ...             def xx(self, extra):
    ...                 return 100 + extra
    ...             foo = 42
    ...         self.cc = CC()
    ...
    ...     localcc = forward_attr('cc', 'xx')
    ...     localfoo = forward_attr('cc', 'foo')
    ...
    >>> print C().localcc(10)
    110
    >>> print C().localfoo
    42

    Arguments: objectName - name of the attribute containing the second object.
               attrName - name of the attribute in the second object.
    Returns:   An object that will forward any calls as described above.
    """
    def __init__(self, objectName, attrName):
        self.objectName = objectName
        self.attrName = attrName

    def __get__(self, instance, owner=None):
        return getattr(getattr(instance, self.objectName), self.attrName)

    def __set__(self, instance, value):
        setattr(getattr(instance, self.objectName), self.attrName, value)

    def __delete__(self, instance):
        delattr(getattr(instance, self.objectName), self.attrName)


class Logger:
    DATE_FMT = "%Y-%m-%d %I:%M:%S%p"
    NORMAL_FMT = "%(asctime)s [%(levelname)s] %(message)s"
    RAW_FMT = "%(message)s"
    WIDTH = 75

    def __init__(self, level="debug", enabled=True):
        """Create and configure logger object.

        Params
        ------
        level (str, default: "debug):  log level
        enabled (bool, default: True): flag to enable log
        """
        if enabled:
            self.handler = logging.StreamHandler(stream=stderr)
        else:
            self.handler = logging.NullHandler()

        self.level = getattr(logging, level.upper())
        self.normal = logging.Formatter(self.NORMAL_FMT, datefmt=self.DATE_FMT)
        self.raw = logging.Formatter(self.RAW_FMT)
        self.logger = logging.getLogger(__package__)
        self.logger.setLevel(self.level)
        self.handler.setLevel(self.level)
        self.logger.addHandler(self.handler)

        self.handler.setFormatter(self.raw)
        self.initmsg()
        self.handler.setFormatter(self.normal)

    def __call__(self, *args, **kwargs):
        """Log a debug message."""
        self.debug(*args, **kwargs)

    def write(self, level=None, *args, **kwargs):
        """Create a formatted log message."""
        if not level:
            level = self.level
        if not isinstance(level, int):
            level = getattr(logging, level)
        self.logger.log(level, self.message(*args, **kwargs))
    debug = partialmethod(write, "DEBUG")
    info = partialmethod(write, "INFO")
    warn = partialmethod(write, "WARNING")
    error = partialmethod(write, "ERROR")
    fatal = partialmethod(write, "FATAL")

    def line(self):
        """Create line in the log."""
        self.write(self.level, style("-" * self.WIDTH, fg="cyan"))

    def initmsg(self):
        """Write a message when logger is created."""
        self.write()
        self.line()
        self.write(self.level, __package__)
        self.line()
        self.write()

    def message(self, *args, **kwargs) -> str:
        """Return a formatted log message.

        Params
        ------
        args:    joined by spaces
        kwargs:  converted to key: value format with keys highlighted
        prefix:  highlighted and prepended to beginning of message
        """
        text = list(args)
        if "prefix" in kwargs:
            prefix = style(kwargs.pop("prefix"), fg="cyan")
            args = [f"{prefix}"]
        if kwargs:
            text += [f"{style(k, fg='yellow')}: {v!r}"
                     for k, v in kwargs.items()]
        if not text:
            return ""

        return " ".join(map(str, text))


Logger.WIDTH = environ.get("COLUMNS", Logger.WIDTH)
log = Logger()
