import os
import asyncio
import logging
from collections import defaultdict, deque

from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream, Update
from pytgcalls.types.stream import StreamAudioEnded
import yt_dlp

load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("MusicBot")

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STRING_SESSION = os.getenv("STRING_SESSION")

bot = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH,
                   session_string=STRING_SESSION)
call = PyTgCalls(assistant)

queues = defaultdict(deque)


def search_youtube(query: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "source_address": "0.0.0.0",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return {
            "url": info["url"],
            "title": info.get("title", "Unknown"),
            "webpage_url": info.get("webpage_url", ""),
        }


async def start_stream(chat_id, track):
    await call.play(chat_id,
                    MediaStream(track["url"],
                                video_flags=MediaStream.Flags.IGNORE))


async def play_next(chat_id):
    if queues[chat_id]:
        track = queues[chat_id].popleft()
        await start_stream(chat_id, track)
        await bot.send_message(
            chat_id,
            f"🎶 **Memutar:** [{track['title']}]({track['webpage_url']})",
            disable_web_page_preview=True)
    else:
        await call.leave_call(chat_id)
        await bot.send_message(chat_id, "✅ Antrian habis, keluar dari VC.")


@call.on_update()
async def stream_end(_, update: Update):
    if isinstance(update, StreamAudioEnded):
        await play_next(update.chat_id)


@bot.on_message(filters.command("start"))
async def start_cmd(_, message: Message):
    await message.reply_text(
        "👋 **Bot Musik Aktif!**\n\n"
        "▶️ `/play <judul/url>` — putar lagu\n"
        "⏭️ `/skip` — lewati lagu\n"
        "⏸️ `/pause` — jeda\n"
        "▶️ `/resume` — lanjut\n"
        "⏹️ `/stop` — berhenti\n"
        "📜 `/queue` — lihat antrian\n\n"
        "Pastikan voice chat sudah aktif & assistant ada di grup!")


@bot.on_message(filters.command("play") & filters.group)
async def play_cmd(_, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply_text("❌ Gunakan: `/play <judul/link>`")

    query = message.text.split(None, 1)[1]
    msg = await message.reply_text("🔎 Mencari lagu...")

    try:
        track = await asyncio.to_thread(search_youtube, query)
    except Exception as e:
        log.error(f"Search error: {e}")
        return await msg.edit_text("❌ Gagal menemukan lagu.")

    try:
        active = chat_id in [c.chat_id for c in call.calls]
    except Exception:
        active = False

    if active:
        queues[chat_id].append(track)
        await msg.edit_text(
            f"➕ **Antrian #{len(queues[chat_id])}:** "
            f"[{track['title']}]({track['webpage_url']})",
            disable_web_page_preview=True)
    else:
        try:
            await start_stream(chat_id, track)
            await msg.edit_text(
                f"🎶 **Memutar:** [{track['title']}]({track['webpage_url']})",
                disable_web_page_preview=True)
        except Exception as e:
            log.error(f"Play error: {e}")
            await msg.edit_text(
                "❌ Gagal. Pastikan VC aktif & assistant join grup.")


@bot.on_message(filters.command("skip") & filters.group)
async def skip_cmd(_, message: Message):
    chat_id = message.chat.id
    try:
        if queues[chat_id]:
            await message.reply_text("⏭️ Lagu dilewati...")
            await play_next(chat_id)
        else:
            await call.leave_call(chat_id)
            await message.reply_text("⏹️ Tidak ada lagu berikutnya.")
    except Exception:
        await message.reply_text("❌ Tidak ada lagu yang diputar.")


@bot.on_message(filters.command("pause") & filters.group)
async def pause_cmd(_, message: Message):
    try:
        await call.pause_stream(message.chat.id)
        await message.reply_text("⏸️ Dijeda. `/resume` untuk lanjut.")
    except Exception:
        await message.reply_text("❌ Tidak ada lagu yang diputar.")


@bot.on_message(filters.command("resume") & filters.group)
async def resume_cmd(_, message: Message):
    try:
        await call.resume_stream(message.chat.id)
        await message.reply_text("▶️ Dilanjutkan.")
    except Exception:
        await message.reply_text("❌ Tidak ada lagu yang dijeda.")


@bot.on_message(filters.command("stop") & filters.group)
async def stop_cmd(_, message: Message):
    chat_id = message.chat.id
    try:
        queues[chat_id].clear()
        await call.leave_call(chat_id)
        await message.reply_text("⏹️ Berhenti & keluar dari VC.")
    except Exception:
        await message.reply_text("❌ Bot tidak di voice chat.")


@bot.on_message(filters.command("queue") & filters.group)
async def queue_cmd(_, message: Message):
    chat_id = message.chat.id
    if not queues[chat_id]:
        return await message.reply_text("📭 Antrian kosong.")
    text = "📜 **Antrian:**\n\n"
    for i, t in enumerate(queues[chat_id], 1):
        text += f"`{i}.` {t['title']}\n"
    await message.reply_text(text)


async def main():
    await assistant.start()
    await call.start()
    await bot.start()
    me = await bot.get_me()
    log.info(f"✅ Bot aktif sebagai @{me.username}")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
