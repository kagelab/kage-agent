from app.database.db import initialize_database
from app.interfaces.irc import KageIRC
from app.config import (
    IRC_SERVER,
    IRC_PORT,
    IRC_NICK
)

def main():
    print(">> 🥷 Iniciando KageAgent v1.1...")
    initialize_database()

    bot = KageIRC()

    print(">> KageIRC iniciado!")
    print(f">> Iniciando o bot: {IRC_NICK}...")
    bot.start()
   
if __name__ == "__main__":
    main()

    