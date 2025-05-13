# meta developer: @FAmods
# description: Показывает статистику твоего аккаунта
# command: .stats - `Получить статистику`

import asyncio
from telethon import events
import logging
from userbot import client, is_owner
from telethon.errors.rpcerrorlist import MessageIdInvalidError

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

async def get_stats(client):
    u_chat = 0
    b_chat = 0
    c_chat = 0
    ch_chat = 0
    all_chats = 0

    async for dialog in client.iter_dialogs():
        all_chats += 1
        if dialog.is_user:
            if dialog.entity.bot:
                b_chat += 1
            elif not dialog.entity.bot:
                u_chat += 1
        elif dialog.is_group:
            c_chat += 1
        elif dialog.is_channel:
            if dialog.entity.megagroup or dialog.entity.gigagroup:
                if dialog.entity.megagroup:
                    c_chat += 1
                elif dialog.entity.gigagroup:
                    c_chat += 1
            elif not dialog.entity.megagroup and not dialog.entity.gigagroup:
                ch_chat += 1
    
    return {
        "all_chats": all_chats,
        "u_chat": u_chat,
        "b_chat": b_chat,
        "c_chat": c_chat,
        "ch_chat": ch_chat
    }

def register_handlers(client):
    """
    Регистрирует обработчики модуля
    """
    @client.on(events.NewMessage(pattern=r'\.stats'))
    async def stats_handler(event):
        """Получить статистику"""
        if not await is_owner(event):
            return
            
        await safe_edit(event, "<blockquote>⚝ зᴀᴦᴩузᴋᴀ ᴄᴛᴀᴛиᴄᴛиᴋи....</blockquote>", parse_mode="html")
        
        try:
            stats = await get_stats(client)
            
            stats_text = f"""<blockquote>⚝ ᴛʙоя ᴄᴛᴀᴛиᴄᴛиᴋᴀ:</blockquote>
<blockquote>⚝ ʙᴄᴇᴦо чᴀᴛоʙ: <code>{stats['all_chats']}</code></blockquote>
<blockquote>⚝ <code>{stats['u_chat']}</code> ᴧичных ᴦᴩуᴨᴨ
⚝ <code>{stats['c_chat']}</code> ᴦᴩуᴨᴨ
⚝ <code>{stats['ch_chat']}</code> ᴋᴀнᴀᴧоʙ
⚝ <code>{stats['b_chat']}</code> боᴛоʙ</blockquote>"""
            
            await safe_edit(event, stats_text, parse_mode="html")
        except Exception as e:
            logger.error(f"Error in stats handler: {str(e)}")
            await safe_edit(event, f"<blockquote>⚝ оɯибᴋᴀ: <code>{str(e)}</code></blockquote>", parse_mode="html")
    
    return stats_handler 