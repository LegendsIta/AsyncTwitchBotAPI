#!/usr/bin/env python
"""
AsyncTwitchBotApi Example Script

This script demonstrates the usage of AsyncTwitchBotApi library to create Twitch chatbots
with customizable commands, filters for execution, and scheduled automatic messages using IRC integration.

Author: LegendsIta <https://github.com/LegendsIta>
"""

from twitchbot import TwitchBot


USERNAME = "YOUR_USERNAME"
OAUTH = "OAUTH"
CHANNEL_NAME = "INSERT_CHANNEL_NAME"

bot = TwitchBot(USERNAME, OAUTH, CHANNEL_NAME)


@bot.scheduler.schedule_task(60, -1)
async def every_minute_schedule():
    """
    Schedule task to send a message every minute indefinitely.

    This function is decorated with bot.scheduler.schedule_task to schedule
    an asynchronous task that sends a message to the Twitch channel every 60 seconds.

    Usage:
        - This function will be called automatically by the bot's scheduler.
    """
    await bot.send_message("This is a every minute schedule...")


@bot.scheduler.schedule_task(10, 5)
async def other_schedule_with_max_repeat():
    """
    Schedule task to send a message every 10 seconds, repeated 5 times.

    This function is decorated with bot.scheduler.schedule_task to schedule
    an asynchronous task that sends a message to the Twitch channel every 10 seconds,
    with a maximum repeat count of 5 times.

    Usage:
        - This function will be called automatically by the bot's scheduler.
    """
    await bot.send_message("This schedule is executed every 10 seconds only 5 times.")


if __name__ == "__main__":
    bot.run()
