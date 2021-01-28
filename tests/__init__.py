from pathlib import Path

__all__ = ["DATADIR", "Stub"]


DATADIR = Path(__file__).parent.joinpath("data")

class Stub:
    """Class for stub objects"""

    def __init__(self, **kwargs):
        """Initialize all kwargs as attributes

        Params
        ------
        klass (type): optional class to set stub instance
        """
        klass = kwargs.pop("klass", None)
        if klass:
            self.__class__ = klass
        for k,v in kwargs.items():
            setattr(self, k, v)
