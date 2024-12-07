from collections import UserList
from csv import DictReader, register_dialect
from pathlib import Path

register_dialect('custom_dialect', skipinitialspace=True)


class CsvFile(UserList):
    """A CSV file that operates as a list and each row is represented as a dictoinary."""

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.loaded = False
        super().__init__()

    def __repr__(self):
        return f"CsvFile <name={self.filepath.name!r}, loaded={self.loaded}, lines={len(self)}>"

    def read(self):
        with open(Path(self.filepath)) as fp:
            reader = DictReader(fp, dialect="custom_dialect")
            for row in reader:
                #  breakpoint()
                self.append(row)
        self.loaded = True
