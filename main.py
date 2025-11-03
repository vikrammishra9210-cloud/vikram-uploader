# TXT Leech Bot - Render-ready
# Put your API_ID, API_HASH, BOT_TOKEN in vars.py OR set them as Render environment variables.
import os
import re
import time
import asyncio
from subprocess import getstatusoutput
from pyrogram import Client, filters
from pyrogram.types import Message
import core as helper
from vars import API_ID, API_HASH, BOT_TOKEN

# Bot client using Bot Token (NO phone login)
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(
        f"Hello {m.from_user.first_name or 'there'}!\n\n"
        "Send /upload to begin the TXT leech process."
    )

@bot.on_message(filters.command("stop"))
async def stop_handler(_, m: Message):
    await m.reply_text("Stopped ✅")
    os._exit(0)

@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    # Ask for TXT file
    msg = await m.reply_text("📄 Please send your .txt file (each link on a new line).")
    file_msg = await bot.listen(m.chat.id)

    if not file_msg.document:
        return await m.reply_text("❌ Please send a valid .txt file (as a document).")

    path = await file_msg.download()
    await file_msg.delete(True)

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.read().splitlines() if ln.strip()]
        os.remove(path)
    except Exception as e:
        return await m.reply_text(f"❌ Could not read file: {e}")

    await msg.edit(f"✅ Found {len(lines)} links. Send starting number (e.g. 1):")
    start_msg = await bot.listen(m.chat.id)
    try:
        start_from = int(start_msg.text.strip())
        if start_from < 1:
            start_from = 1
    except:
        start_from = 1
    await start_msg.delete(True)

    await msg.edit("✅ Send Batch Name (short text):")
    batch_msg = await bot.listen(m.chat.id)
    batch_name = batch_msg.text.strip() or "batch"
    await batch_msg.delete(True)

    await msg.edit("✅ Send Quality (144/240/360/480/720/1080). Send 'best' for auto:")
    q_msg = await bot.listen(m.chat.id)
    quality = q_msg.text.strip()
    await q_msg.delete(True)

    await msg.edit("✅ Send Caption (or 'no'):")
    cap_msg = await bot.listen(m.chat.id)
    caption = cap_msg.text if cap_msg.text.lower() != "no" else ""
    await cap_msg.delete(True)

    await msg.edit("✅ Send thumbnail URL or 'no':")
    thumb_msg = await bot.listen(m.chat.id)
    thumb = thumb_msg.text.strip()
    await thumb_msg.delete(True)
    if thumb.startswith("http"):
        getstatusoutput(f"wget '{thumb}' -O thumb.jpg")
        thumb_file = "thumb.jpg"
    else:
        thumb_file = None

    await msg.edit("⏳ Starting downloads... I will upload to this chat when each file is ready.")

    count = start_from
    for idx in range(start_from - 1, len(lines)):
        url = lines[idx]
        try:
            # Clean name
            name_clean = re.sub(r'[^A-Za-z0-9 _-]', '', url)[:40].strip()
            video_name = f"{str(count).zfill(3)} {batch_name} {name_clean}"

            if quality.lower() == "best":
                cmd = f'yt-dlp -o "{video_name}.%(ext)s" "{url}"'
            else:
                # Build yt-dlp format for height if you gave numeric like 720
                if quality.isdigit():
                    q = int(quality)
                    cmd = f'yt-dlp -f "bestvideo[height<={q}]+bestaudio/best" -o "{video_name}.mp4" "{url}"'
                else:
                    cmd = f'yt-dlp -f "best" -o "{video_name}.mp4" "{url}"'

            await m.reply_text(f"⬇️ Downloading: {video_name}")
            # Run download (blocking) - yt-dlp should be installed in image
            os.system(cmd)

            # Find downloaded file (simple heuristic)
            found = None
            for ext in ("mp4","mkv","webm","mp3","m4a","pdf","m4v"):
                candidate = f"{video_name}.{ext}"
                if os.path.exists(candidate):
                    found = candidate
                    break

            if not found:
                # try glob for video_name*
                import glob
                gl = glob.glob(f"{video_name}.*")
                found = gl[0] if gl else None

            if not found:
                await m.reply_text(f"❌ Download failed for: {url}")
                count += 1
                continue

            # Send file (video or document)
            if found.lower().endswith(('.mp4', '.mkv', '.webm', '.mov', '.m4v')):
                await helper.send_vid(bot, m, caption or None, found, thumb_file, video_name, None)
            else:
                await bot.send_document(chat_id=m.chat.id, document=found, caption=caption or None)

            try:
                os.remove(found)
            except:
                pass

            count += 1
            time.sleep(1)

        except Exception as e:
            await m.reply_text(f"❌ Error processing {url}: {e}")
            count += 1
            continue

    await m.reply_text("✅ All done!")
    if thumb_file and os.path.exists(thumb_file):
        try:
            os.remove(thumb_file)
        except:
            pass

if __name__ == '__main__':
    bot.run()
