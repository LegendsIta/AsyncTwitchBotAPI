from twitchbot.irc import IRCClient
from twitchbot._scheduler import Scheduler
import logging
import asyncio
from twitchbot.types import Sender

bot_log = logging.getLogger("TwitchBOT")
chat_log = logging.getLogger("TwitchCHAT")


class TwitchBot(IRCClient):
    def __init__(self, username: str, oauth: str, channel: str):
        super().__init__(username, oauth)
        self._channel = channel
        self._messages_handlers = []
        self._scheduler = Scheduler()

    @property
    def scheduler(self):
        return self._scheduler

    @staticmethod
    def _build_handler_dict(handler, **filters):
        return {
            'function': handler,
            'filters': {ftype: fvalue for ftype, fvalue in filters.items() if fvalue is not None}
        }

    def message_handler(self, messages: list = None, func=None):
        def decorator(handler):
            nonlocal messages
            if messages is None:
                messages = [handler.__name__]
            self._messages_handlers.append(self._build_handler_dict(handler, commands=messages, func=func))
            return handler

        return decorator

    async def _call_handlers(self, sender: Sender, message: str = None, args: list = None):
        for message_handler in self._messages_handlers:
            filters = message_handler["filters"]
            if message in filters["commands"]:
                if "func" in filters and filters["func"](sender) is False:
                    continue
                bot_log.info(f"{sender.username} performed {message} args({args})")
                task = asyncio.create_task(message_handler["function"](sender, args))
                task.add_done_callback(self._handle_task_result)
                await asyncio.sleep(0.1)
                return True
        return None

    async def _run_task(self):
        bot_log.info("Connecting to Twitch server...")
        await self.connect()
        await self.join_channel(self._channel)
        task = asyncio.create_task(self._scheduler.run())
        task.add_done_callback(self._handle_task_result)
        while True:
            resp = await self.get_response()
            if "PRIVMSG" in resp:
                sender = Sender(resp)
                data = sender.message.rstrip().split(" ")
                if data and len(data) > 0:
                    cmd = data[0]
                    args = data[1:]
                    if not await self._call_handlers(sender, cmd.lower(), args):
                        chat_log.info(sender.username + ": " + sender.message)

            else:
                bot_log.info(resp)

    @staticmethod
    def _handle_task_result(task):
        try:
            task.result()
        except Exception as e:
            bot_log.error(f'Task raised an exception: {e}')

    def run(self):
        bot_log.info("Runnig TwitchBOT...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._run_task())
        bot_log.info("TwithBot closed!")
