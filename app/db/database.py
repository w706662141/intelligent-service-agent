import sqlite3

from app.config.database_config import DATABASE_PATH

_conn = None


def get_connection():
    global _conn

    if _conn is None:
        _conn = sqlite3.connect(DATABASE_PATH)

    return _conn