from datetime import datetime

from app.database.models import (
    create_task,
    get_task,
    get_tasks_for_date,
    complete_task,
    delete_task,
    edit_task
)

# Formato da data e hora usado pelo bot
DATE_FORMAT = "%d-%m-%Y"
TIME_FORMAT = "%H:%M"

def today():
    return datetime.now().strftime(DATE_FORMAT)

def format_task(task):
    status = {
        "pending": "⏳ pendente",
        "done": "✅ concluído",
        "skipped": "⏭️ adiado",
        "cancelled": "❌ cancelado"
    }.get(task["status"], "?")

    return (
        f'{status} #{task["id"]} '
        f'{task["task_time"]} '
        f'{task["title"]}'
    )

def add_task_command(args):
    parts = args.split(maxsplit=2)

    if len(parts) < 3:
        return (
            "[Uso] = !add DATA HORA TAREFA | "
            "ex: !add 05-09-2026 14:00 Estudar Terraform"
        )

    task_date = parts[0]
    task_time = parts[1]
    title = parts[2]

    try:
        # Transforma a data e hora nos formatos definidos acima
        datetime.strptime(task_date, DATE_FORMAT)
        datetime.strptime(task_time, TIME_FORMAT)
    except ValueError:
        return (
            "[!] Data ou hora inválida. "
            "Use DD-MM-YYYY HH:MM."
        )

    task_id = create_task(
        title=title,
        task_date=task_date,
        task_time=task_time
    )

    return (
        f"[OK] Tarefa #{task_id} criada: "
        f"{task_date} às {task_time} - {title}"
    )

def agenda_command():
    date = today()
    tasks = get_tasks_for_date(date)

    if not tasks:
        return "[FREE] Nenhuma tarefa para hj."

    # pega somente as últimas 5 horários da lista de tarefas
    tasks = tasks[-5:]
    
    result = [
        f"[TODO] Agenda de {date}:"
    ]

    for task in tasks:
        result.append(
            format_task(task)
        )

    return result

def done_command(args):
    try:
        task_id = int(args.strip())
    except ValueError:
        return "[Uso] = !done ID"

    task = get_task(task_id)

    if not task:
        return f"[!] Tarefa #{task_id} não encontrada."

    if complete_task(task_id):
        return (
            f"[OK] Tarefa #{task_id} concluída: "
            f"{task['title']}"
        )
    
    return "[!] Não foi possível concluir a tarefa."

def delete_command(args):
    try:
        task_id = int(args.strip())
    except ValueError:
        return "[Uso] = !delete ID"
        
    task = get_task(task_id)
    if not task:
        return f"[!] Tarefa #{task_id} não encontrada."

    if delete_task(task_id):
        return (
            f"[OK] Tarefa #{task_id} removida: "
            f"{task['title']}"
        )

    return "[!] Não foi possível remover a tarefa."

def edit_command(args):
    parts = args.split(maxsplit=2)

    if len(parts) < 3:
        return (
            "[Uso] = !edit ID HORA NOVO_NOME | "
            "ex: !edit 12 15:00 Estudar Python"            
        )

    try:
        task_id = int(parts[0])
        task_time = parts[1]
    except ValueError:
        return "[!] ID ou hora inválida."
    
    title = parts[2]

    try:
        datetime.strptime(
            task_time,
            TIME_FORMAT
        )
    except ValueError:
        return "[!] Hora inválida. Use HH:MM."

    task = get_task(task_id)

    if not task:
        return f"[!] Tarefa #{task_id} não encontrada."

    edit_task(
        task_id,
        title=title,
        task_time=task_time
    )            

    return (
        f"[OK] Tarefa #{task_id} alterada: "
        f"{task_time} - {title}"
    )
    
def process_command(command, args):
    command = command.lower()

    if command == "!add":
        return add_task_command(args)

    if command == "!agenda":
        return agenda_command()

    if command == "!done":
        return done_command(args)

    if command == "!delete":
        return delete_command(args)

    if command == "!edit":
        return edit_command(args)

    if command == "!help":
        return (
            "!add DATA HORA TAREFA *** "
            "!agenda *** "
            "!done ID *** "
            "!edit ID HORA TAREFA *** "
            "!delete ID"
        )

    return None
    
