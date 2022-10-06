import atexit
import sqlite3
from pathlib import Path

from ._sql_stetments import CREATE_TABLES_STATEMENT

db_file = Path("deprecation-notifier-db.sqlite")
db_created = not db_file.exists()
connection = sqlite3.connect(db_file)


def create_tables(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()
    cursor.execute(CREATE_TABLES_STATEMENT)


if db_created:
    create_tables(connection)


def get_pending_conflicts():
    raise NotImplementedError  # TODO


@atexit.register
def close_connection() -> None:
    global connection
    connection.close()
