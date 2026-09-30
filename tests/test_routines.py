import sqlite3

from app.tasks import routines

def test_edit_routine_schedule(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"

    def get_test_connection():
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row 
        return connection

    monkeypatch.setattr(routines, "get_connection", get_test_connection)
    connection = get_test_connection()
    connection.executescript(
        """
        CREATE TABLE routines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL DEFAULT 'active'
        );

        CREATE TABLE routine_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        routine_id INTEGER NOT NULL,
        day TEXT NOT NULL,
        start_time TEXT,
        end_time TEXT,
        FOREIGN KEY(routine_id)
            REFERENCES routines(id)
        );
        """
    )

    routine_id = connection.execute(
        """
        INSERT INTO routines (title)
        VALUES (?)
        """,
        ("Karatê",),
    ).lastrowid

    schedule_id = connection.execute(
        """
        INSERT INTO routine_schedule (
        routine_id,
        day,
        start_time,
        end_time
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            routine_id,
            "MON",
            "17:45",
            "18:45",
        ),
    ).lastrowid

    connection.commit()
    connection.close()

    changed = routines.edit_routine_schedule(
        schedule_id,
        day="WED",
    )

    assert changed is True

    connection = get_test_connection()
    schedule = connection.execute(
        """
        SELECT * FROM routine_schedule
        WHERE id = ?
        """,
        (schedule_id,),
    ).fetchone()

    connection.close()

    assert schedule["day"] == "WED"
    assert schedule["start_time"] == "17:45"
    assert schedule["end_time"] == "18:45"
