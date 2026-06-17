from pyrogram import Client, filters
from dotenv import load_dotenv
import os

load_dotenv()

bot = Client(
    "bot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

@bot.on_message(filters.command("start"))
async def start(_, message):
    print("START COMMAND DITERIMA")
    await message.reply_text("✅ BOT HIDUP")

@bot.on_message(filters.command("ping"))
async def ping(_, message):
    print("PING COMMAND DITERIMA")
    await message.reply_text("🏓 PONG")

print("BOT STARTING...")
bot.run()
