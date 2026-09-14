from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from app.database.models import (
    get_pending_reminders,
    mark_reminder_sent
)
from app.config import TIMEZONE

class TaskScheduler:
    def __init__(self, send_message):
        self.send_message = send_message
        self.scheduler = BackgroundScheduler()

    def start(self):
        self.scheduler.add_job(
            self.check_tasks,
            "interval",
            seconds=30, # Verifica as tarefas a cada 30 segundos
            id="task_checker",
            replace_existing=True
        )
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()

    def check_tasks(self):
        now = datetime.now(TIMEZONE).replace(tzinfo=None)
        # Busca os avisos pendentes
        reminders = get_pending_reminders()
        for reminder in reminders:
            remind_at = datetime.strptime(
                reminder["remind_at"],
                "%d-%m-%Y %H:%M"
            )
            delay = now - remind_at
            if delay > timedelta(minutes=2):
                mark_reminder_sent(reminder["id"])

            elif remind_at <= now:
                if reminder["reminder_type"] == "before":
                    message = (
                        f"[TODO](Em Breve): {reminder['title']} "
                        f"às {reminder['task_time']}"
                    )
                elif reminder["reminder_type"] == "at_time":
                    message = (
                        f"[TODO](Agora): "
                        f"#{reminder['task_id']} "
                        f"{reminder['title']}"
                    )

                self.send_message(message)
                mark_reminder_sent(reminder["id"])
      