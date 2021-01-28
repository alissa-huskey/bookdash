from pathlib import Path

__all__ = ["DATADIR"]


DATADIR = Path(__file__).parent.joinpath("data")
