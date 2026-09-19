from app.database.db import get_connection

DAY_ORDER = {
    "MON": 0,
    "TUE": 1,
    "WED": 2,
    "THU": 3,
    "FRI": 4,
    "SAT": 5,
    "SUN": 6,
}

def create_routine(title, description=None):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO routines (
            title,
            description
        )
        VALUES (?, ?)
        """,
        (
            title,
            description
        )
    )

    # Pega o ID que o sqlite acabou de gerar
    routine_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return routine_id


def add_routine_schedule(
    routine_id,
    day,
    start_time=None, # rotina com horários flexíveis
    end_time=None
):
    connection = get_connection()

    cursor = connection.execute(
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
            day,
            start_time,
            end_time
        )
    )

    schedule_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return schedule_id


def get_routines():
    connection = get_connection()

    routines = connection.execute(
        """
        SELECT *
        FROM routines
        WHERE status = 'active'
        ORDER BY id
        """
    ).fetchall()

    connection.close()
    return routines


def get_routine_schedules(routine_id):
    connection = get_connection()

    schedules = connection.execute(
        """
        SELECT *
        FROM routine_schedule
        WHERE routine_id = ?
        """,
        (routine_id,)
    ).fetchall()

    # ordena os dias pelo DAY_ORDER e horários
    schedules = sorted(
        schedules,
        key=lambda schedule: (
            DAY_ORDER[schedule["day"]],
            schedule["start_time"]
        )
    )

    connection.close()
    return schedules


def delete_routine(routine_id):
    connection = get_connection()

    connection.execute(
        """
        DELETE FROM routine_schedule
        WHERE routine_id = ?
        """,
        (routine_id,)
    )

    cursor = connection.execute(
        """
        DELETE FROM routines
        WHERE id = ?
        """,
        (routine_id,)
    )

    connection.commit()
    # retorna True se o número de linhas apagadas for > 0
    changed = cursor.rowcount > 0
    connection.close()

    return changed
