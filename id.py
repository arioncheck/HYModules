# meta developer: @codrago_m
# description: Инструмент для получения ID пользователей и чатов
# command: .id - `Получить ваш ID`
# command: .userid - `Получить ID пользователя`
# command: .chatid - `Получить ID чата`

import logging
from telethon import events, types
from userbot import client, is_owner

logger = logging.getLogger(__name__)

def register_handlers(client):
    @client.on(events.NewMessage(pattern=r'\.id'))
    async def id_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            
            try:
                user = await client.get_entity(event.sender_id)
                
                result_message = f"<blockquote>⚝ инфоᴩʍᴀция об ID</blockquote>\n\n" \
                                f"<blockquote>⚝ ʙᴀɯ ниᴋ: <code>{user.first_name}</code>\n" \
                                f"⚝ ʙᴀɯ ID: <code>{event.sender_id}</code></blockquote>"
                
                if can_edit:
                    await event.edit(result_message, parse_mode="html")
                else:
                    await event.respond(result_message, parse_mode="html")
                
            except Exception as e:
                error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
                if can_edit:
                    await event.edit(error_message, parse_mode="html")
                else:
                    await event.respond(error_message, parse_mode="html")
                    
        except Exception as e:
            logger.error(f"Ошибка в id_handler: {str(e)}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if event.out:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")
    
    @client.on(events.NewMessage(pattern=r'\.userid'))
    async def userid_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            args = event.text.split(' ', 1)[1] if len(event.text.split(' ', 1)) > 1 else None
            reply = await event.get_reply_message()
            
            try:
                if args:
                    user = await client.get_entity(int(args) if args.isdigit() else args)
                elif reply:
                    user = await client.get_entity(reply.sender_id)
                else:
                    error_message = "<blockquote>⚝ нᴇᴛ ᴩᴇᴨᴧᴀя нᴀ ᴄообщᴇниᴇ</blockquote>"
                    if can_edit:
                        await event.edit(error_message, parse_mode="html")
                    else:
                        await event.respond(error_message, parse_mode="html")
                    return
                    
                if isinstance(user, types.User):
                    result_message = f"<blockquote>⚝ инфоᴩʍᴀция о ᴨоᴧьзоʙᴀᴛᴇᴧᴇ</blockquote>\n\n" \
                                     f"<blockquote>⚝ иʍя: <code>{user.first_name}</code>\n" \
                                     f"⚝ ID ᴨоᴧьзоʙᴀᴛᴇᴧя: <code>{user.id}</code></blockquote>"
                else:
                    if hasattr(user, 'title'):
                        if hasattr(user, 'username') and user.username:
                            channel_id = f"-100{user.id}"
                        else:
                            channel_id = f"{user.id}"
                            
                        result_message = f"<blockquote>⚝ инфоᴩʍᴀция о ᴋᴀнᴀᴧᴇ/чᴀᴛᴇ</blockquote>\n\n" \
                                         f"<blockquote>⚝ нᴀзʙᴀниᴇ: <code>{user.title}</code>\n" \
                                         f"⚝ ID ᴋᴀнᴀᴧᴀ/чᴀᴛᴀ: <code>{channel_id}</code></blockquote>"
                    else:
                        result_message = f"<blockquote>⚝ инфоᴩʍᴀция о ᴨоᴧьзоʙᴀᴛᴇᴧᴇ</blockquote>\n\n" \
                                         f"<blockquote>⚝ ID: <code>{user.id}</code></blockquote>"
                
                if can_edit:
                    await event.edit(result_message, parse_mode="html")
                else:
                    await event.respond(result_message, parse_mode="html")
                
            except Exception as e:
                error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
                if can_edit:
                    await event.edit(error_message, parse_mode="html")
                else:
                    await event.respond(error_message, parse_mode="html")
                    
        except Exception as e:
            logger.error(f"Ошибка в userid_handler: {str(e)}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if event.out:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")
    
    @client.on(events.NewMessage(pattern=r'\.chatid'))
    async def chatid_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            
            try:
                if not event.is_group and not event.is_channel:
                    error_message = "<blockquote>⚝ эᴛо нᴇ чᴀᴛ</blockquote>"
                    if can_edit:
                        await event.edit(error_message, parse_mode="html")
                    else:
                        await event.respond(error_message, parse_mode="html")
                    return
                
                if hasattr(event.chat, 'title'):
                    chat_title = event.chat.title
                else:
                    chat_title = "Чат"
                
                if hasattr(event.peer_id, 'channel_id'):
                    chat_id = f"-100{event.peer_id.channel_id}"
                else:
                    chat_id = str(event.chat_id)
                
                result_message = f"<blockquote>⚝ инфоᴩʍᴀция о чᴀᴛᴇ</blockquote>\n\n" \
                                 f"<blockquote>⚝ нᴀзʙᴀниᴇ: <code>{chat_title}</code>\n" \
                                 f"⚝ ID чᴀᴛᴀ: <code>{chat_id}</code></blockquote>"
                
                if can_edit:
                    await event.edit(result_message, parse_mode="html")
                else:
                    await event.respond(result_message, parse_mode="html")
                
            except Exception as e:
                error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
                if can_edit:
                    await event.edit(error_message, parse_mode="html")
                else:
                    await event.respond(error_message, parse_mode="html")
                    
        except Exception as e:
            logger.error(f"Ошибка в chatid_handler: {str(e)}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if event.out:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")
    
    return [id_handler, userid_handler, chatid_handler] 