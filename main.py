import os
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "GpmsMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text(
        "🎵 Halo!\n\n"
        "Saya adalah GPMS Music Bot.\n\n"
        "Perintah yang tersedia:\n"
        "/ping - Cek bot\n"
        "/help - Bantuan"
    )

@app.on_message(filters.command("help"))
async def help_cmd(_, message: Message):
    await message.reply_text(
        "📖 Bantuan:\n\n"
        "/start\n"
        "/ping\n"
        "/help"
    )

@app.on_message(filters.command("ping"))
async def ping(_, message: Message):
    await message.reply_text("🏓 Pong!")

print("Bot berhasil dijalankan...")
app.run()
