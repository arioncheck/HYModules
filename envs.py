# meta developer: @qveroz
# description: Загрузка файлов на хостинг envs.sh и получение прямой ссылки
# command: .envs - `Ответьте на сообщение с файлом/текстом для загрузки на envs.sh`

import os
import io
import requests
import aiohttp
import asyncio
from telethon import events
from userbot import client

def register_handlers(client):
    """
    Загрузка файлов на хостинг envs.sh и получение прямой ссылки
    """
    @client.on(events.NewMessage(pattern=r'\.envs'))
    async def envs_handler(event):
        """Ответьте на сообщение с файлом/текстом для загрузки на envs.sh"""
        try:
            reply = await event.get_reply_message()
            if not reply:
                await event.edit("<blockquote>оᴛʙᴇᴛь нᴀ ᴄообщᴇниᴇ иᴧи ɸᴀйᴧ!</blockquote>", parse_mode="html")
                return

            await event.edit("<blockquote>зᴀᴦᴩузᴋᴀ ɸᴀйᴧᴀ...</blockquote>", parse_mode="html")

            if reply.media:
                file = io.BytesIO(await client.download_media(reply.media, bytes))
                if hasattr(reply.media, "document"):
                    file.name = reply.file.name or f"file_{reply.file.id}"
                else:
                    file.name = f"file_{reply.id}.jpg"
            else:
                file = io.BytesIO(bytes(reply.raw_text, "utf-8"))
                file.name = "text.txt"
            
            response = requests.post("https://envs.sh", files={"file": file})
            if response.status_code == 200:
                file_url = response.text.strip()
                await event.edit(f"<blockquote>⚝ ᴄᴄыᴧᴋᴀ: {file_url}</blockquote>", parse_mode="html")
            else:
                await event.edit("<blockquote>Error uploading file</blockquote>", parse_mode="html")
                
        except Exception as e:
            await event.edit(f"<blockquote>Error: {str(e)}</blockquote>", parse_mode="html")

    return envs_handler 