import irc.bot
import time
from app.config import (
    IRC_SERVER,
    IRC_PORT,
    IRC_CHANNEL,
    IRC_NICK
)
from app.tasks.manager import process_command
from app.tasks.scheduler import TaskScheduler

class KageIRC(irc.bot.SingleServerIRCBot):
    def __init__(self):
        print(f">> Conectando a {IRC_SERVER}...")
        super().__init__(
            [
                (
                    IRC_SERVER,
                    IRC_PORT,
                    None
                )
            ],
            IRC_NICK,
            IRC_NICK
        )

        self.channel = IRC_CHANNEL
        self.scheduler = TaskScheduler(
            self.send_scheduler_message
        )
    
    def on_welcome(
        self,
        connection,
        event
    ):
        connection.join(self.channel)
        print(f">> Entrando no canal {self.channel}...")
        self.scheduler.start()

        connection.privmsg(
            self.channel,
            f"🥷 KageAgent v1.1 online."
        )

        connection.privmsg(
            self.channel,
            "[?] Digite !help para saber os comandos."
        )

    def on_pubmsg(
        self,
        connection,
        event
    ):
        message = event.arguments[0]

        if not message.startswith("!"):
            return
        
        parts = message.split(
            maxsplit=1
        )
        command = parts[0]
        args = ""

        if len(parts) > 1:
            args = parts[1]

        response = process_command(
            command,
            args
        )

        if response:
            if isinstance(response, list):
                for response_message in response:
                    connection.privmsg(
                        event.target,
                        response_message
                    )
                    time.sleep(2)
            else:
                connection.privmsg(
                    event.target,
                    response
                )

    def send_scheduler_message(
        self,
        message
    ):
        connection = self.connection

        if connection:
            connection.privmsg(
                self.channel,
                message
            )
            