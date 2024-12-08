"""Database module."""

from functools import cached_property

from sqlmodel import Field, Session, SQLModel, create_engine, select

from bookdash.config import Config

bp = breakpoint


class DB():
    """Database class."""

    config = Config()

    DB_FILE = Config().data_dir / "library.db"

    @property
    def sqlite_url(self):
        """Return the sqlite database URL.

        For example: sqlite:////library.db
        """
        uri = self.DB_FILE.absolute().as_uri()
        sqlite_url = f"sqlite:/{uri[5:]}"
        return sqlite_url

    @property
    def engine(self):
        """Return a database engine."""
        self.DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        return create_engine(
            self.sqlite_url,
            echo=True,
            connect_args={"check_same_thread": False},
        )

    @property
    def session(self):
        """Return the database session."""
        return Session(self.engine)

    def create(self):
        """Create SQL database and tables."""
        SQLModel.metadata.create_all(self.engine)
