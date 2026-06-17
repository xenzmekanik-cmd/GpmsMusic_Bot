from pyrogram import Client, filters
from dotenv import load_dotenv
from collections import defaultdict, deque
import os

load_dotenv()

bot = Client(
    "bot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

queues = defaultdict(deque)

@bot.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text("✅ BOT HIDUP")

@bot.on_message(filters.command("ping"))
async def ping(_, message):
    await message.reply_text("🏓 PONG")

@bot.on_message(filters.command("play"))
async def play(_, message):

    if len(message.command) < 2:
        return await message.reply_text(
            "Contoh:\n/play Alan Walker Faded"
        )

    lagu = message.text.split(None, 1)[1]

    queues[message.chat.id].append(lagu)

    await message.reply_text(
        f"🎵 Ditambahkan ke antrian:\n{lagu}"
    )

@bot.on_message(filters.command("queue"))
async def queue(_, message):

    q = queues[message.chat.id]

    if not q:
        return await message.reply_text("📭 Queue kosong")

    text = "📜 Queue:\n\n"

    for i, lagu in enumerate(q, start=1):
        text += f"{i}. {lagu}\n"

    await message.reply_text(text)

print("BOT STARTING...")
bot.run()
