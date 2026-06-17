from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STRING_SESSION = os.getenv("STRING_SESSION")

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

assistant = Client(
    "assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

call = PyTgCalls(assistant)

@bot.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text("✅ BOT HIDUP")

@bot.on_message(filters.command("ping"))
async def ping(_, message):
    await message.reply_text("🏓 PONG")

async def main():
    print("STARTING BOT...")
    await assistant.start()
    print("ASSISTANT ONLINE")

    await call.start()
    print("PYTGCALLS ONLINE")

    await bot.start()

    me = await bot.get_me()
    print(f"BOT ONLINE @{me.username}")

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
