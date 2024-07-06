#!/usr/bin/env python
#
# AsyncTwitchBotApi is a library that enables you to create Twitch chatbots with customizable commands,
# filters for execution, and scheduled automatic messages using IRC integration.
#
# Author: LegendsIta <https://github.com/LegendsIta>
#
"""This module contains an object that represents a Twitch Subscription of Twitch Sender."""

from twitchbot import TwitchBot
from twitchbot.types import Sender


USERNAME = "YOUR_USERNAME"
OAUTH = "OAUTH"
CHANNEL_NAME = "INSERT_CHANNEL_NAME"

bot = TwitchBot(USERNAME, OAUTH, CHANNEL_NAME)


@bot.message_handler(messages=["!test", "!alias1", "!alias2"], func=lambda sender: sender.username == USERNAME)
async def test_filtered(sender: Sender, args):
    await bot.send_message("Test command with filter!")


@bot.message_handler(messages=["!command"])
async def test_basic(sender: Sender, args):
    await bot.send_message(sender.username + " performed a basic command!")


if __name__ == "__main__":
    bot.run()
