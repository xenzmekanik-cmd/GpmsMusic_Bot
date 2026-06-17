import os
import asyncio
import logging
from collections import defaultdict, deque

from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
import yt_dlp

load_dotenv()

logging.basicConfig(level=logging.INFO)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STRING_SESSION = os.getenv("STRING_SESSION")

bot = Client(
    "music_bot",
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

queues = defaultdict(deque)


def search_youtube(query):
    opts = {
        "format": "bestaudio/best",
        "default_search": "ytsearch",
        "noplaylist": True,
        "quiet": True
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        data = ydl.extract_info(query, download=False)

        if "entries" in data:
            data = data["entries"][0]

        return {
            "title": data["title"],
            "url": data["url"],
            "webpage_url": data["webpage_url"]
        }


@bot.on_message(filters.command("start"))
async def start_cmd(_, message: Message):
    await message.reply_text(
        "🎵 Bot Musik Aktif!\n\n"
        "/play <judul>\n"
        "/skip\n"
        "/pause\n"
        "/resume\n"
        "/stop\n"
        "/queue"
    )


@bot.on_message(filters.command("play") & filters.group)
async def play_cmd(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Gunakan:\n/play nama lagu"
        )

    query = message.text.split(None, 1)[1]

    msg = await message.reply_text("🔍 Mencari lagu...")

    try:
        track = await asyncio.to_thread(
            search_youtube,
            query
        )

        queues[message.chat.id].append(track)

        await msg.edit_text(
            f"✅ Ditambahkan:\n{track['title']}"
        )

    except Exception as e:
        await msg.edit_text(f"Error:\n{e}")


@bot.on_message(filters.command("queue"))
async def queue_cmd(_, message: Message):

    q = queues[message.chat.id]

    if not q:
        return await message.reply_text(
            "📭 Queue kosong"
        )

    text = "📜 Queue:\n\n"

    for i, song in enumerate(q, start=1):
        text += f"{i}. {song['title']}\n"

    await message.reply_text(text)


@bot.on_message(filters.command("skip"))
async def skip_cmd(_, message: Message):
    if queues[message.chat.id]:
        queues[message.chat.id].popleft()

    await message.reply_text("⏭ Skip")


@bot.on_message(filters.command("stop"))
async def stop_cmd(_, message: Message):
    queues[message.chat.id].clear()
    await message.reply_text("⏹ Stop")


async def main():
    await assistant.start()
    await call.start()
    await bot.start()

    me = await bot.get_me()

    print(f"Bot aktif: @{me.username}")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
