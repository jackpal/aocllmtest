import sqlite3
from sqlite3 import Connection
import datetime
from aoc_api import model_families, models

def create_or_open_puzzle_db(db_name: str = "puzzle.db") -> Connection:
    """Creates the puzzle.db database if it doesn't exist, otherwise opens it.

    Also registers the modern datetime adapter and initializes ModelFamilies and Models tables.

    Args:
        db_name: The name of the database file.

    Returns:
        A sqlite3.Connection object.
    """

    sqlite3.register_adapter(datetime.datetime, lambda val: val.isoformat())
    sqlite3.register_converter("TIMESTAMP", lambda val: datetime.datetime.fromisoformat(val.decode()))

    conn = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    # Create tables if they don't exist
    with open("schema.sql", "r") as f:
        schema = f.read()
    cursor.executescript(schema)

    # Initialize ModelFamilies and Models tables
    for family in model_families():
        cursor.execute("INSERT OR IGNORE INTO ModelFamilies (model_family) VALUES (?)", (family,))
        for model in models(family):  # models() now returns a list
            cursor.execute("INSERT OR IGNORE INTO Models (model_name, model_family) VALUES (?, ?)", (model, family))

    conn.commit()
    return conn
