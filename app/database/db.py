import os
import sqlite3
from app.config import DATABASE_PATH

def get_connection():
    directory = os.path.dirname(DATABASE_PATH)

    if directory:
        os.makedirs(directory, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            task_date TEXT NOT NULL,
            task_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            priority TEXT NOT NULL DEFAULT 'normal',
            created_at TEXT NOT NULL,
            completed_at TEXT
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            remind_at TEXT NOT NULL,
            sent INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(task_id)
                REFERENCES tasks(id)
        )
        """
    )

    # Verifica se a coluna reminder_type já existe
    query = """
        SELECT COUNT(*)
        FROM pragma_table_info(?)
        WHERE name = ?
    """

    result = connection.execute(
        query,
        ("reminders", "reminder_type")
    ).fetchone()

    # Se não existir, adiciona
    if result[0] == 0:
        connection.execute(
            """
            ALTER TABLE reminders
            ADD COLUMN reminder_type TEXT
            """
        )

    connection.commit()
    connection.close()
    