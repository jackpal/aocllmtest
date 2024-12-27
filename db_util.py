import sqlite3
from sqlite3 import Connection
import datetime

def create_or_open_puzzle_db(db_name: str = "puzzle.db") -> Connection:
    """Creates the puzzle.db database if it doesn't exist, otherwise opens it.

    Also registers the modern datetime adapter.

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
    with open("schema.sql", "r") as f:  # Assuming you save the schema as schema.sql
        schema = f.read()
    cursor.executescript(schema)
    conn.commit()

    return conn
