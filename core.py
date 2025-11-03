# Minimal helper functions used by main.py
import os
import asyncio

async def send_vid(bot, m, caption, filename, thumb, name, prog):
    # Send video using pyrogram. Use send_video for videos and send_document otherwise.
    try:
        await bot.send_video(chat_id=m.chat.id, video=filename, caption=caption or '', thumb=thumb)
    except Exception as e:
        # fallback to document
        await bot.send_document(chat_id=m.chat.id, document=filename, caption=caption or '')
