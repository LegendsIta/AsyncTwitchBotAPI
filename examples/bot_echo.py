from twitchbot import TwitchBot
from twitchbot.types import Sender


USERNAME = "YOUR_USERNAME"
OAUTH = "OAUTH"
CHANNEL_NAME = "INSERT_CHANNEL_NAME"

bot = TwitchBot(USERNAME, OAUTH, CHANNEL_NAME)


@bot.message_handler()
async def echo(sender: Sender, args):
    await bot.send_message(" ".join(args))


if __name__ == "__main__":
    bot.run()
