from bookdash.db import DB


def test_db():
    db = DB()
    assert db
