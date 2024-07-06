#!/usr/bin/env python
"""
AsyncTwitchBotApi Example Script

This script demonstrates the usage of AsyncTwitchBotApi library to create Twitch chatbots
with customizable commands, filters for execution, and scheduled automatic messages using IRC integration.

Author: LegendsIta <https://github.com/LegendsIta>
"""

from typing import List
from twitchbot import TwitchBot
from twitchbot.types import Sender


USERNAME = "YOUR_USERNAME"
OAUTH = "OAUTH"
CHANNEL_NAME = "INSERT_CHANNEL_NAME"

bot = TwitchBot(USERNAME, OAUTH, CHANNEL_NAME)


@bot.message_handler()
async def echo(sender: Sender, args: List[str]):
    """
    Message handler function that echoes back a message.

    This function is decorated with bot.message_handler to handle incoming messages from Twitch chat.
    It echoes back the received message by joining the arguments into a single string and sending it.

    Args:
        sender (Sender): Object containing information about the message sender.
        args (List[str]): List of arguments received in the message.

    Usage:
        - This function will be called automatically by the bot when a message is received.
    """
    await bot.send_message(" ".join(args))


if __name__ == "__main__":
    bot.run()
