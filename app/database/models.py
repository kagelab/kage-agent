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
