import sqlite3
from functools import lru_cache

from terminal_gpt.settings import DB_PATH


@lru_cache()
def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH.as_posix())
