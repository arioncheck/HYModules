# meta developer: @qveroz
# description: Показывает статистику личного чата
# command: .lst - `Получить статистику личного чата`

import asyncio
from telethon import events
import logging
from userbot import client, is_owner
from telethon.errors.rpcerrorlist import MessageIdInvalidError
from telethon.tl.types import User, Channel, Chat
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def safe_edit(event, text, **kwargs):
    try:
        await event.edit(text, **kwargs)
    except MessageIdInvalidError:
        try:
            await event.respond(text, **kwargs)
        except Exception as e:
            logger.error(f"Error responding to message: {str(e)}")
    except Exception as e:
        logger.error(f"Error editing message: {str(e)}")

async def ensure_connection():
    try:
        if not client.is_connected():
            logger.info("Client not connected, connecting...")
            await client.connect()
            
        if not await client.is_user_authorized():
            logger.error("Client not authorized")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error ensuring connection: {str(e)}")
        return False

async def get_chat_stats(event, limit=1000):
    """Получает статистику сообщений в текущем чате"""
    
    if not await ensure_connection():
        return {
            "is_private": False,
            "error": "Нет подключения к Telegram"
        }
    
    try:
        chat = await event.get_chat()
    except Exception as e:
        logger.error(f"Error getting chat: {str(e)}")
        return {
            "is_private": False,
            "error": f"Ошибка получения чата: {str(e)}"
        }
    
    if not isinstance(chat, User):
        return {
            "is_private": False
        }
    
    try:
        me = await client.get_me()
    except Exception as e:
        logger.error(f"Error getting me: {str(e)}")
        return {
            "is_private": False,
            "error": f"Ошибка получения информации о себе: {str(e)}"
        }
    
    my_messages = 0
    other_messages = 0
    total_messages = 0
    
    last_week_messages = 0
    last_month_messages = 0
    
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    try:
        async for message in client.iter_messages(chat, limit=limit):
            total_messages += 1
            
            if message.sender_id == me.id:
                my_messages += 1
            else:
                other_messages += 1
            
            if message.date.replace(tzinfo=None) > week_ago:
                last_week_messages += 1
            
            if message.date.replace(tzinfo=None) > month_ago:
                last_month_messages += 1
    except Exception as e:
        logger.error(f"Error iterating messages: {str(e)}")
        return {
            "is_private": False,
            "error": f"Ошибка при сборе сообщений: {str(e)}"
        }
    
    my_percent = round((my_messages / total_messages) * 100, 1) if total_messages > 0 else 0
    other_percent = round((other_messages / total_messages) * 100, 1) if total_messages > 0 else 0
    
    if hasattr(chat, 'first_name'):
        other_name = f"{chat.first_name} {chat.last_name if chat.last_name else ''}".strip()
    else:
        other_name = "Собеседник"
    
    return {
        "is_private": True,
        "total_messages": total_messages,
        "my_messages": my_messages,
        "other_messages": other_messages,
        "my_percent": my_percent,
        "other_percent": other_percent,
        "last_week_messages": last_week_messages,
        "last_month_messages": last_month_messages,
        "other_name": other_name
    }

def register_handlers(client):
    """
    Регистрирует обработчики модуля
    """
    @client.on(events.NewMessage(pattern=r'\.lst'))
    async def lst_handler(event):
        """Получить статистику личного чата"""
        if not await is_owner(event):
            return
        
        if not await ensure_connection():
            await safe_edit(event, "<blockquote>⚝ нᴇᴛ ᴨодᴋᴧючᴇния ᴋ Telegram.</blockquote>", parse_mode="html")
            return
        
        try:
            chat = await event.get_chat()
            if not isinstance(chat, User):
                await safe_edit(event, "<blockquote>⚝ ᴋоʍᴀндᴀ ᴩᴀбоᴛᴀᴇᴛ ᴛоᴧьᴋо ʙ ᴧичных чᴀᴛᴀх.</blockquote>", parse_mode="html")
                return
        except Exception as e:
            logger.error(f"Error getting chat: {str(e)}")
            await safe_edit(event, f"<blockquote>⚝ оɯибᴋᴀ ᴨоᴧучᴇния чᴀᴛᴀ: <code>{str(e)}</code></blockquote>", parse_mode="html")
            return
        
        await safe_edit(event, "<blockquote>⚝ ᴄобиᴩᴀю ᴄᴛᴀᴛиᴄᴛиᴋу...</blockquote>", parse_mode="html")
        
        try:
            stats = await get_chat_stats(event)
            
            if not stats.get("is_private", False):
                if "error" in stats:
                    await safe_edit(event, f"<blockquote>⚝ оɯибᴋᴀ: <code>{stats['error']}</code></blockquote>", parse_mode="html")
                else:
                    await safe_edit(event, "<blockquote>⚝ ᴋоʍᴀндᴀ ᴩᴀбоᴛᴀᴇᴛ ᴛоᴧьᴋо ʙ ᴧичных чᴀᴛᴀх.</blockquote>", parse_mode="html")
                return
            
            stats_text = f"""<blockquote>⚝ ᴄᴛᴀᴛиᴄᴛиᴋᴀ чᴀᴛᴀ ᴄ <code>{stats['other_name']}</code>:</blockquote>

<blockquote>⚝ ʙᴄᴇᴦо ᴄообщᴇний: <code>{stats['total_messages']}</code></blockquote>
<blockquote>⚝ ᴛʙои ᴄообщᴇния: <code>{stats['my_messages']}</code></blockquote>
<blockquote>⚝ ᴄообщᴇния ᴄобᴇᴄᴇдниᴋᴀ: <code>{stats['other_messages']}</code></blockquote>
<blockquote>⚝ ᴄообщᴇний зᴀ нᴇдᴇᴧю: <code>{stats['last_week_messages']}</code></blockquote>
<blockquote>⚝ ᴄообщᴇний зᴀ ʍᴇᴄяц: <code>{stats['last_month_messages']}</code></blockquote>"""
            
            await safe_edit(event, stats_text, parse_mode="html")
        except Exception as e:
            logger.error(f"Error in lst handler: {str(e)}")
            await safe_edit(event, f"<blockquote>⚝ оɯибᴋᴀ: <code>{str(e)}</code></blockquote>", parse_mode="html")
    
    return lst_handler 