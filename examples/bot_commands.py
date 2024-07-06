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


@bot.message_handler(messages=["!test", "!alias1", "!alias2"], func=lambda sender: sender.username == USERNAME)
async def test_filtered(sender: Sender, args: List[str]):
    """
    Filtered message handler function for specific commands.

    This function is decorated with bot.message_handler to handle incoming messages from Twitch chat
    that match the specified commands and filter condition.

    This function will be called only if the func function returns true,
    in this case a lambda function checks that the message is sent by a specific username

    Args:
        sender (Sender): Object containing information about the message sender.
        args (list): List of arguments received in the message.

    Usage:
        - This function will be called automatically by the bot when a matching message is received.
    """
    await bot.send_message("Test command with filter!")


@bot.message_handler(messages=["!command"])
async def test_basic(sender: Sender, args: List[str]):
    """
    Basic message handler function for a specific command.

    This function is decorated with bot.message_handler to handle incoming messages from Twitch chat
    that match the specified command.

    Args:
        sender (Sender): Object containing information about the message sender.
        args (list): List of arguments received in the message.

    Usage:
        - This function will be called automatically by the bot when a matching message is received.
    """
    await bot.send_message(sender.username + " performed a basic command!")


if __name__ == "__main__":
    bot.run()
