import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

load_dotenv()

IRC_SERVER = os.getenv("IRC_SERVER")
IRC_PORT = int(os.getenv("IRC_PORT"))
IRC_CHANNEL = os.getenv("IRC_CHANNEL")
IRC_NICK = os.getenv("IRC_NICK")

DATABASE_PATH = os.getenv("DATABASE_PATH", "data/kage.db")

# Minutos antes da tarefa para enviar o aviso
REMINDER_MINUTES = int(os.getenv("REMINDER_MINUTES","15"))

# Pega o timezone do .env com ZoneInfo
TIMEZONE = ZoneInfo(os.getenv("TIMEZONE", "UTC"))
