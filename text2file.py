# meta developer: @hikka_mods
# description: Модуль для конвертации текста в файл
# command: .ttf - `Конвертировать текст в файл`

import io
import logging
import re
import os
from telethon import events
from userbot import client, is_owner

logger = logging.getLogger(__name__)

FILE_EXTENSIONS = {
    'txt': 'text/plain',
    'py': 'text/x-python',
    'js': 'text/javascript',
    'html': 'text/html',
    'css': 'text/css',
    'json': 'application/json',
    'xml': 'application/xml',
    'md': 'text/markdown',
    'csv': 'text/csv',
    'cfg': 'text/plain',
    'ini': 'text/plain',
    'log': 'text/plain',
    'sh': 'text/x-sh',
    'bat': 'text/plain',
    'c': 'text/x-c',
    'cpp': 'text/x-c++',
    'h': 'text/x-c',
    'java': 'text/x-java',
    'php': 'application/x-php',
}

def register_handlers(client):
    @client.on(events.NewMessage(pattern=r'\.ttf(?:\s+(.+))?'))
    async def ttf_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            args = event.pattern_match.group(1)
            
            file_name = "file.txt"
            
            if not args:
                reply = await event.get_reply_message()
                if reply:
                    text = reply.message
                    
                    if reply.file and hasattr(reply.file, 'name') and reply.file.name:
                        file_name = reply.file.name
                else:
                    error_message = "<blockquote>⚝ нᴇдоᴄᴛᴀᴛочно ᴀᴩᴦуʍᴇнᴛоʙ! Иᴄᴨоᴧьзуйᴛᴇ: .ttf ᴛᴇᴋᴄᴛ/ᴋод</blockquote>"
                    if can_edit:
                        await event.edit(error_message, parse_mode="html")
                    else:
                        await event.respond(error_message, parse_mode="html")
                    return
            else:
                file_match = re.match(r'^([^|]+)\|(.+)$', args, re.DOTALL)
                if file_match:
                    file_name = file_match.group(1).strip()
                    text = file_match.group(2).strip()
                else:
                    text = args
            
            if '.' not in file_name:
                file_name += '.txt'
                
            ext = file_name.split('.')[-1].lower()
                
            preparing_message = f"<blockquote>⚝ ᴄоздᴀю фᴀйᴧ <code>{file_name}</code>...</blockquote>"
            
            if can_edit:
                message = await event.edit(preparing_message, parse_mode="html")
            else:
                message = await event.respond(preparing_message, parse_mode="html")
            
            try:
                file_bytes = io.BytesIO(text.encode("utf-8"))
                file_bytes.name = file_name
                
                await message.delete()
                
                attributes = None
                
                await event.respond(
                    f"<blockquote>⚝ фᴀйᴧ: <code>{file_name}</code></blockquote>", 
                    file=file_bytes, 
                    parse_mode="html",
                    attributes=attributes
                )
            except Exception as e:
                error_message = f"<blockquote>⚝ оɯибᴋᴀ ᴨᴩи ᴄоздᴀнии фᴀйᴧᴀ: {str(e)}</blockquote>"
                if can_edit:
                    await message.edit(error_message, parse_mode="html")
                else:
                    await event.respond(error_message, parse_mode="html")
                
        except Exception as e:
            logger.error(f"Ошибка в ttf_handler: {str(e)}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if event.out:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")
    
    return [ttf_handler] 