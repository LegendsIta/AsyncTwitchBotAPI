from twitchbot import TwitchBot


USERNAME = "YOUR_USERNAME"
OAUTH = "OAUTH"
CHANNEL_NAME = "INSERT_CHANNEL_NAME"

bot = TwitchBot(USERNAME, OAUTH, "CHANNEL_NAME")


@bot.scheduler.schedule_task(60, -1)
async def every_minute_schedule():
    await bot.send_message("This is a every minute schedule...")


@bot.scheduler.schedule_task(10, 5)
async def other_schedule_with_max_repeat():
    await bot.send_message("This schedule is executed every 10 seconds only 5 times.")

if __name__ == "__main__":
    bot.run()
