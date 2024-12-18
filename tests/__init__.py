"""Test module."""

from pathlib import Path

import pytest
from confz import DataSource

__all__ = ["DATADIR", "Stub"]


DATADIR = Path(__file__).parent.joinpath("data")


class Stub:
    """Class for stub objects."""

    def __init__(self, **kwargs):
        """Initialize all kwargs as attributes.

        Params
        ------
        klass (type): optional class to set stub instance
        """
        klass = kwargs.pop("klass", None)
        if klass:
            self.__class__ = klass
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, name):
        """Return None if attr is missing."""
        return None


def get_filecontents(filename):
    """Return the contents of a file."""
    with open(DATADIR.joinpath(filename)) as fp:
        contents = fp.read()
    return contents


def data_source(**kwargs):
    """Return a confz.DataSource source."""
    return DataSource(dict(**kwargs))
