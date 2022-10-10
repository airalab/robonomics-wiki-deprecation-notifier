import atexit
import sqlite3
from pathlib import Path

from ._sql_stetments import CREATE_TABLES_STATEMENT

db_file = Path("deprecation-notifier-db.sqlite")
connection = sqlite3.connect(db_file)


def create_tables(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()
    cursor.execute(CREATE_TABLES_STATEMENT)
    connection.commit()


create_tables(connection)


@atexit.register
def close_connection() -> None:
    global connection
    connection.close()
