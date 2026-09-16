from datetime import datetime, timedelta
from app.database.db import get_connection
from app.config import REMINDER_MINUTES

def create_task(
    title,
    task_date,
    task_time,
    description=None,
    priority="normal"
):
    connection = get_connection()
    now = datetime.now().isoformat(timespec="seconds")
    cursor = connection.execute(
        """
        INSERT INTO tasks (
            title,
            description,
            task_date,
            task_time,
            status,
            priority,
            created_at
        )
        VALUES (?, ?, ?, ?, 'pending', ?, ?)
        """,
        (
            title,
            description,
            task_date,
            task_time,
            priority,
            now
        )
    )

    task_id = cursor.lastrowid

    # Converte a data e hora da tarefa em um objeto datetime
    task_datetime = datetime.strptime(
        f"{task_date} {task_time}",
        "%d-%m-%Y %H:%M"
    )

    # Horário do aviso antes da tarefa
    reminder_time = (
        task_datetime - timedelta(minutes=REMINDER_MINUTES)
    )

    reminder_time = reminder_time.strftime(
        "%d-%m-%Y %H:%M"
    )

    create_reminder(
        connection,
        task_id,
        reminder_time,
        "before"
    )

    create_reminder(
        connection,
        task_id,
        task_datetime.strftime("%d-%m-%Y %H:%M"),
        "at_time"
    )

    connection.commit()
    connection.close()
    return task_id


def get_task(task_id):
    connection = get_connection()
    task = connection.execute(
        """
        SELECT *
        FROM tasks 
        WHERE id = ?
        """,
        (task_id,)
    ).fetchone()

    connection.close()
    return task


def get_tasks_for_date(task_date):
    connection = get_connection()
    tasks = connection.execute(
        """
        SELECT *
        FROM tasks
        WHERE task_date = ?
        ORDER BY task_time ASC
        """,
        (task_date,)
    ).fetchall()

    connection.close()
    return tasks


def complete_task(task_id):
    connection = get_connection()
    now = datetime.now().isoformat(timespec="seconds")
    cursor = connection.execute(
        """
        UPDATE tasks
        SET status = 'done',
            completed_at = ?
        WHERE id = ?
        """,
        (now, task_id)
    )

    connection.commit()
    changed = cursor.rowcount > 0
    connection.close()
    return changed


def delete_task(task_id):
    connection = get_connection()
    cursor = connection.execute(
        """
        DELETE FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    )

    connection.commit()
    changed = cursor.rowcount > 0
    connection.close()
    return changed


def edit_task(
    task_id,
    title=None,
    task_date=None,
    task_time=None
):
    connection = get_connection()
    task = connection.execute(
        """
        SELECT *
        FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    ).fetchone()

    if not task:
        connection.close()
        return False

    new_title = title or task["title"]
    new_date = task_date or task["task_date"]
    new_time = task_time or task["task_time"]

    # Verifica se a nova data e horário é diferente da antiga
    schedule_changed = (
        new_date != task["task_date"]
        or new_time != task["task_time"]
    )

    if schedule_changed:
        connection.execute(
            """
            DELETE from reminders
            WHERE task_id = ?
            """,
            (task_id,)
        )

        task_datetime = datetime.strptime(
            f"{new_date} {new_time}",
            "%d-%m-%Y %H:%M"
        )

        # Horário do aviso antes da tarefa
        reminder_time = (
            task_datetime - timedelta(minutes=REMINDER_MINUTES)
        )

        # transforma a data e hora da tarefa e aviso em string
        task_datetime_str = task_datetime.strftime("%d-%m-%Y %H:%M")
        reminder_time_str = reminder_time.strftime(
            "%d-%m-%Y %H:%M"
        )

        create_reminder(
            connection,
            task_id,
            reminder_time_str,
            "before"
        )

        create_reminder(
            connection,
            task_id,
            task_datetime_str,
            "at_time"
        )

    connection.execute(
        """
        UPDATE tasks
        SET title = ?,
            task_date = ?,
            task_time = ?
        WHERE id = ?
        """,
        (
            new_title,
            new_date,
            new_time,
            task_id,
        )
    )

    connection.commit()
    connection.close()
    return True


def create_reminder(
    # Recebe a conexão existente do banco para reutilizar
    connection,
    task_id,
    remind_at,
    reminder_type
):
    cursor = connection.execute(
        """
        INSERT INTO reminders (
            task_id,
            remind_at,
            reminder_type,
            sent
        )
        VALUES (?, ?, ?, 0)
        """,
        (
            task_id,
            remind_at,
            reminder_type
        )
    )

    reminder_id = cursor.lastrowid
    return reminder_id


# Busca os avisos ainda não enviados 
def get_pending_reminders():
    connection = get_connection()
    cursor = connection.execute(
        """
        SELECT reminders.*,
               tasks.title,
               tasks.task_time
        FROM reminders
        JOIN tasks
            ON reminders.task_id = tasks.id
        WHERE reminders.sent = 0
        ORDER BY reminders.remind_at
        """
    )
    reminders = cursor.fetchall()
    connection.close()
    return reminders


# Marca o aviso como enviado para não ficar repetindo
def mark_reminder_sent(reminder_id):
    connection = get_connection()
    cursor = connection.execute(
        """
        UPDATE reminders
        SET sent = 1
        WHERE id = ?
        """,
        (reminder_id,)
    )
    # Salva a alteração no banco
    connection.commit()
    connection.close()


# v2
def create_routine(title, description=None):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO routines (
            title,
            description,
            status
        )
        VALUES (?, ?, 'active')
        """,
        (
            title,
            description
        )
    )

    routine_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return routine_id


def add_routine_schedule(
        routine_id,
        day,
        start_time = None,
        end_time = None
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


def get_routine_schedule(routine_id):
    connection = get_connection()

    schedules = connection.execute(
        """
        SELECT *
        FROM routine_schedule
        WHERE routine_id = ?
        ORDER BY id
        """,
        (routine_id,)
    ).fetchall()

    connection.close()

    return schedules


def get_active_routines():
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


def edit_routine_schedule(
        schedule_id,
        day=None,
        start_time=None,
        end_time=None
):
    connection = get_connection()
    schedule = connection.execute(
        """
        SELECT *
        FROM routine_schedule
        WHERE id = ?
        """,
        (schedule_id,)
    ).fetchone()

    if not schedule:
        connection.close()
        return False

    new_day = day or schedule["day"]
    new_start_time = start_time or schedule["start_time"]
    new_end_time = end_time or schedule["end_time"]

    connection.execute(
        """
        UPDATE routine_schedule
        SET day = ?,
            start_time = ?,
            end_time = ?
        WHERE id = ?
        """,
        (
            new_day,
            new_start_time,
            new_end_time,
            schedule_id
        )
    )

    connection.commit()
    connection.close()

    return True
