import sqlite3
from contextlib import contextmanager
from app.config.database_config import DATABASE_PATH
from app.db.database_pools import POOL

_conn = None


def get_connection():
    global _conn

    if _conn is None:
        _conn = sqlite3.connect(DATABASE_PATH)

    return _conn


@contextmanager
def get_mysql_connection():
    conn = POOL.connect()
    try:
        yield conn
    finally:
        conn.close()
