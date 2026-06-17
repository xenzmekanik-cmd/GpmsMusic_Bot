from pyrogram import Client, filters
import os
from dotenv import load_dotenv

load_dotenv()

bot = Client(
    "bot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

@bot.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "✅ Bot berhasil online"
    )

@bot.on_message(filters.command("ping"))
async def ping(_, message):
    await message.reply_text("🏓 PONG")

print("BOT STARTED")
bot.run()
