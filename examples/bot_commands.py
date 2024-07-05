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


@bot.scheduler.schedule_task(60, -1)
async def test_schedule():
    await bot.send_message("Basic scheduled messages...")


if __name__ == "__main__":
    bot.run()
