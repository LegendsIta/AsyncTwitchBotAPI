#!/usr/bin/env python
#
# AsyncTwitchBotApi is a library that enables you to create Twitch chatbots with customizable commands,
# filters for execution, and scheduled automatic messages using IRC integration.
#
# Author: LegendsIta <https://github.com/LegendsIta>
#
"""This module provides a Twitch chatbot with message handling and scheduling capabilities."""

from twitchbot.irc import IRCClient
from twitchbot._scheduler import Scheduler
import logging
import asyncio
from twitchbot.types import Sender
import signal


bot_log = logging.getLogger("TwitchBOT")
chat_log = logging.getLogger("TwitchCHAT")


class TwitchBot(IRCClient):
    """
    TwitchBot class extends IRCClient to create a Twitch chat bot with message handling and scheduling capabilities.

    Attributes:
        _channel (str): The Twitch channel name where the bot operates.
        _messages_handlers (list): List of message handler dictionaries with function and filter information.
        _scheduler (Scheduler): Scheduler instance for managing scheduled tasks.
        _running (bool): Flag indicating if the bot is currently running.

    Methods:
        __init__(username: str, oauth: str, channel: str):
            Initializes TwitchBot instance with Twitch credentials and channel name.

        message_handler(messages: list = None, func=None):
            Decorator method to register message handling functions with optional filters.

        _call_handlers(sender: Sender, args: list[str]) -> Optional[bool]:
            Asynchronously calls registered message handlers based on filters and sender information.

        _run_task():
            Main asynchronous task that connects to Twitch, joins the channel, and handles incoming messages.

        _handle_task_result(task):
            Handles results (including exceptions) of asynchronous tasks.

        run():
            Starts running the TwitchBot instance, connecting it to Twitch and handling messages and scheduled tasks.

        stop():
            Stops the TwitchBot instance, disconnecting from Twitch and stopping all scheduled tasks.
    """
    def __init__(self, username: str, oauth: str, channel: str):
        """
        Initializes TwitchBot instance with Twitch credentials and channel name.

        Args:
              username (str): Twitch bot's username.
              oauth (str): OAuth token for authentication.
             channel (str): Twitch channel name where the bot will operate.
        """
        super().__init__(username, oauth)
        self._channel = channel
        self._messages_handlers = []
        self._scheduler = Scheduler()
        self._running = False
        signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(self._sigint_sigterm_handler(s, f)))
        signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(self._sigint_sigterm_handler(s, f)))

    async def _sigint_sigterm_handler(self, signal, frame):
        """
        Handles SIGINT and SIGTERM signals gracefully by stopping the bot.

        Args:
            signal: Signal received (SIGINT or SIGTERM).
            frame: Frame object representing the stack frame at the time of the signal.
         """
        await self.stop()

    @staticmethod
    def _build_handler_dict(handler, **filters):
        """
        Helper method to build a dictionary containing a message handler function and its associated filters.

        Args:
            handler: Message handler function.
            **filters: Keyword arguments representing filters for the handler.

        Returns:
            dict: Dictionary containing 'function' (handler function) and 'filters' (dictionary of filters).
        """
        return {
            'function': handler,
            'filters': {ftype: fvalue for ftype, fvalue in filters.items() if fvalue is not None}
        }

    def message_handler(self, messages: list = None, func=None):
        """
        Decorator method to register message handling functions with optional filters.

        Args:
            messages (list, optional): List of specific messages (commands) to trigger the handler.
            func (callable, optional): Function to filter whether the handler should be called.

        Returns:
            callable: Decorator function that registers the message handler.
        """
        def decorator(handler):
            nonlocal messages
            self._messages_handlers.append(self._build_handler_dict(handler, commands=messages, func=func))
            return handler

        return decorator

    async def _call_handlers(self, sender: Sender, args: list[str]):
        """
        Asynchronously calls registered message handlers based on filters and sender information.

        Args:
            sender (Sender): Sender object containing information about the message sender.
            args (list[str]): List of arguments parsed from the message.

        Returns:
            Optional[bool]: True if a handler was called successfully, False if not, None if no handlers matched.
        """
        cmd = args[0]
        cmd_args = args[1:]
        for message_handler in self._messages_handlers:
            filters = message_handler["filters"]
            if ("commands" in filters and cmd in filters["commands"]) or not "commands" in filters:
                if "func" in filters and filters["func"](sender) is False:
                    continue
                if "commands" in filters:
                    bot_log.info(f"{sender.username} performed {message_handler['function'].__name__}(!{cmd}) args({cmd_args})")
                else:
                    bot_log.info(f"{sender.username} performed {message_handler['function'].__name__} with {args}")

                task = asyncio.create_task(message_handler["function"](sender, cmd_args if "commands" in filters else args))
                task.add_done_callback(self._handle_task_result)
                await asyncio.sleep(0.1)
                return True

        return None

    async def _run_task(self):
        """
        Main asynchronous task that connects to Twitch, joins the channel, and handles incoming messages.
        """
        bot_log.info("Connecting to Twitch server...")
        await self.connect()
        await self.join_channel(self._channel)
        task = asyncio.create_task(self._scheduler.run())
        task.add_done_callback(self._handle_task_result)
        while self._running:
            resp = await self.get_response()
            if "PRIVMSG" in resp:
                sender = Sender(resp)
                args = sender.message.rstrip().split(" ")
                if args and len(args) > 0:
                    if not await self._call_handlers(sender, args):
                        chat_log.info(sender.username + ": " + sender.message)

            elif len(resp) > 0:
                bot_log.info(resp)

    @staticmethod
    def _handle_task_result(task):
        """
        Handles results (including exceptions) of asynchronous tasks.

        Args:
            task: Asynchronous task object.
        """
        try:
            task.result()
        except Exception as e:
            bot_log.error(f'Task raised an exception: {e}')

    def run(self):
        """
        Starts running the TwitchBot instance, connecting it to Twitch and handling messages and scheduled tasks.
        """
        self._running = True
        bot_log.info("Runnig TwitchBOT...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._run_task())

    async def stop(self):
        """
        Stops the TwitchBot instance, disconnecting from Twitch and stopping all scheduled tasks.
        """
        bot_log.info("Stopping TwitchBOT...")
        self._running = False
        self.scheduler.stop()
        await self.disconnect()  # Wait for IRC disconnect to complete
        # Ensure all scheduled tasks are properly awaited
        tasks = [task() for task in self._scheduler._scheduled_tasks]  # Assuming Scheduler exposes tasks properly
        await asyncio.gather(*tasks)
        asyncio.get_event_loop().stop()

    @property
    def scheduler(self):
        """
        Property to access the Scheduler instance used for managing scheduled tasks.

        Returns:
            Scheduler: Instance of the Scheduler class.
        """
        return self._scheduler
