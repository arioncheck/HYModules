# meta developer: @shrimp_mod
# description: Подсчет сообщений, медиа и статистики пользователей в чате
# command: .mymsg - `Подсчитывает ваши сообщения и медиафайлы`
# command: .usermsg - `Подсчитывает сообщения указанного пользователя`
# command: .allmsg - `Подсчитывает сообщения всех участников`
# command: .chatstats - `Показывает полную статистику чата`
# command: .silent - `Получает список пользователей без сообщений`

import logging
from telethon import events, functions, types
from userbot import client, is_owner

logger = logging.getLogger(__name__)

def register_handlers(client):
    async def get_message_stats(chat_id, user_id, is_private=False):
        """Подсчет сообщений и медиа для чатов и ЛС"""
        stats = {
            "total_messages": 0,
            "stickers": 0,
            "gifs": 0,
            "photos": 0,
            "videos": 0,
            "voice": 0,
            "documents": 0,
            "total_media": 0
        }
        
        try:
            messages_count = await client(functions.messages.SearchRequest(
                peer=chat_id,
                q="",
                filter=types.InputMessagesFilterEmpty(),
                min_date=None,
                max_date=None,
                offset_id=0,
                add_offset=0,
                limit=0,
                max_id=0,
                min_id=0,
                from_id=user_id,
                hash=0
            ))
            total_messages = getattr(messages_count, 'count', 0)
            if total_messages == 0 and hasattr(messages_count, 'messages'):
                total_messages = len(messages_count.messages)
        except Exception as e:
            logger.error(f"Error counting messages: {e}")
            total_messages = 0

        offset_id = 0
        limit = 100
        collected_messages = 0

        while collected_messages < total_messages and collected_messages < 1000:  
            try:
                if is_private:
                    history = await client(functions.messages.GetHistoryRequest(
                        peer=chat_id,
                        offset_id=offset_id,
                        offset_date=None,
                        add_offset=0,
                        limit=limit,
                        max_id=0,
                        min_id=0,
                        hash=0
                    ))
                    messages = history.messages
                else:
                    messages = await client(functions.messages.SearchRequest(
                        peer=chat_id,
                        q="",
                        filter=types.InputMessagesFilterEmpty(),
                        min_date=None,
                        max_date=None,
                        offset_id=offset_id,
                        add_offset=0,
                        limit=limit,
                        max_id=0,
                        min_id=0,
                        from_id=user_id,
                        hash=0
                    ))
                    messages = messages.messages

                if not messages:
                    break

                for msg in messages:
                    sender_id = getattr(msg.from_id, 'user_id', None)
                    if sender_id is None and hasattr(msg, 'sender_id'):
                        sender_id = msg.sender_id
                        
                    if sender_id == user_id:
                        stats["total_messages"] += 1
                        collected_messages += 1
                        
                        if getattr(msg, 'sticker', None):
                            stats["stickers"] += 1
                            stats["total_media"] += 1
                        elif hasattr(msg.media, 'document') and getattr(msg.media.document, 'mime_type', '').startswith('video/mp4') and getattr(msg.media.document, 'attributes', []) and any(getattr(attr, 'round_message', False) for attr in msg.media.document.attributes):
                            stats["gifs"] += 1
                            stats["total_media"] += 1
                        elif getattr(msg, 'photo', None):
                            stats["photos"] += 1
                            stats["total_media"] += 1
                        elif getattr(msg, 'video', None) or (hasattr(msg.media, 'document') and getattr(msg.media.document, 'mime_type', '').startswith('video/')):
                            stats["videos"] += 1
                            stats["total_media"] += 1
                        elif hasattr(msg.media, 'document') and getattr(msg.media.document, 'mime_type', '').startswith('audio/ogg'):
                            stats["voice"] += 1
                            stats["total_media"] += 1
                        elif getattr(msg, 'document', None) or (hasattr(msg, 'media') and hasattr(msg.media, 'document')):
                            stats["documents"] += 1
                            stats["total_media"] += 1

                if not messages:
                    break
                offset_id = messages[-1].id
            except Exception as e:
                logger.error(f"Error processing messages batch: {e}")
                break

        stats["total_messages"] = total_messages

        return stats

    async def get_chat_participants(chat_id):
        """Получение всех участников чата"""
        try:
            return await client.get_participants(chat_id)
        except Exception as e:
            logger.error(f"Error getting participants: {e}")
            return []

    async def get_chat_total_stats(chat_id):
        """Получение общей статистики чата"""
        stats = {
            "total_messages": 0,
            "total_members": 0,
            "admins": 0,
            "deleted_accounts": 0,
            "media_messages": 0
        }
        
        try:
            participants = await get_chat_participants(chat_id)
            stats["total_members"] = len(participants)
            stats["deleted_accounts"] = len([u for u in participants if u.deleted])
            stats["admins"] = len([u for u in participants if u.participant and getattr(u.participant, 'admin_rights', None)])

            messages = await client(functions.messages.SearchRequest(
                peer=chat_id,
                q="",
                filter=types.InputMessagesFilterEmpty(),
                min_date=None,
                max_date=None,
                offset_id=0,
                add_offset=0,
                limit=0,
                max_id=0,
                min_id=0,
                hash=0
            ))
            
            stats["total_messages"] = getattr(messages, 'count', 0)
            if stats["total_messages"] == 0 and hasattr(messages, 'messages'):
                stats["total_messages"] = len(messages.messages)

            media_messages = await client(functions.messages.SearchRequest(
                peer=chat_id,
                q="",
                filter=types.InputMessagesFilterPhotoVideo(),
                min_date=None,
                max_date=None,
                offset_id=0,
                add_offset=0,
                limit=0,
                max_id=0,
                min_id=0,
                hash=0
            ))
            
            stats["media_messages"] = getattr(media_messages, 'count', 0)
            if stats["media_messages"] == 0 and hasattr(media_messages, 'messages'):
                stats["media_messages"] = len(media_messages.messages)
        except Exception as e:
            logger.error(f"Error getting chat stats: {e}")
            
        return stats

    @client.on(events.NewMessage(pattern=r'\.mymsg'))
    async def mymsg_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            
            chat_id = event.chat_id
            chat = await client.get_entity(chat_id)
            is_private = chat_id == (await client.get_me()).id or getattr(chat, 'first_name', None) is not None
            chat_title = getattr(chat, 'title', None) or f"{is_private and 'личном чате' or 'этом канале'}"

            waiting_message = "<blockquote>⚝ нᴀчинᴀю ᴨодᴄчᴇᴛ ʙᴀɯих ᴄообщᴇний...\nЭᴛо ʍожᴇᴛ зᴀняᴛь нᴇᴋоᴛоᴩоᴇ ʙᴩᴇʍя</blockquote>"
            
            if can_edit:
                message = await event.edit(waiting_message, parse_mode="html")
            else:
                message = await event.respond(waiting_message, parse_mode="html")
            
            stats = await get_message_stats(chat_id, (await client.get_me()).id, is_private=is_private)
            
            result = f"<blockquote>⚝ ʙᴀɯᴀ ᴄᴛᴀᴛиᴄᴛиᴋᴀ ʙ {chat_title}</blockquote>\n\n" \
                    f"<blockquote>⚝ ʙᴄᴇᴦо ᴄообщᴇний: <code>{stats['total_messages']}</code>\n" \
                    f"⚝ ʙᴄᴇᴦо ʍᴇдиᴀᴋонᴛᴇнᴛᴀ: <code>{stats['total_media']}</code>\n" \
                    f"⚝ ᴄᴛиᴋᴇᴩоʙ: <code>{stats['stickers']}</code>\n" \
                    f"⚝ GIF: <code>{stats['gifs']}</code>\n" \
                    f"⚝ фоᴛо: <code>{stats['photos']}</code>\n" \
                    f"⚝ ʙидᴇо: <code>{stats['videos']}</code>\n" \
                    f"⚝ ᴦоᴧоᴄоʙых: <code>{stats['voice']}</code>\n" \
                    f"⚝ фᴀйᴧоʙ: <code>{stats['documents']}</code></blockquote>"
            
            if can_edit:
                await message.edit(result, parse_mode="html")
            else:
                await message.respond(result, parse_mode="html")
                
        except Exception as e:
            logger.error(f"Error in mymsg_handler: {e}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if event.out:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")

    @client.on(events.NewMessage(pattern=r'\.usermsg'))
    async def usermsg_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            
            chat_id = event.chat_id
            chat = await client.get_entity(chat_id)
            is_private = chat_id == (await client.get_me()).id or getattr(chat, 'first_name', None) is not None
            chat_title = getattr(chat, 'title', None) or f"{is_private and 'личном чате' or 'этом канале'}"

            args = event.text.split(' ', 1)[1] if len(event.text.split(' ', 1)) > 1 else None
            reply = await event.get_reply_message()
            
            if reply:
                user = await client.get_entity(reply.sender_id)
            elif args:
                try:
                    user = await client.get_entity(args)
                except Exception:
                    error_message = "<blockquote>⚝ нᴇ удᴀᴧоᴄь нᴀйᴛи ᴨоᴧьзоʙᴀᴛᴇᴧя</blockquote>"
                    if can_edit:
                        await event.edit(error_message, parse_mode="html")
                    else:
                        await event.respond(error_message, parse_mode="html")
                    return
            else:
                error_message = "<blockquote>⚝ уᴋᴀжиᴛᴇ ᴨоᴧьзоʙᴀᴛᴇᴧя иᴧи оᴛʙᴇᴛьᴛᴇ нᴀ ᴄообщᴇниᴇ</blockquote>"
                if can_edit:
                    await event.edit(error_message, parse_mode="html")
                else:
                    await event.respond(error_message, parse_mode="html")
                return
                
            username = f"@{user.username}" if getattr(user, 'username', None) else f"{user.first_name}"

            waiting_message = f"<blockquote>⚝ нᴀчинᴀю ᴨодᴄчᴇᴛ ᴄообщᴇний ᴨоᴧьзоʙᴀᴛᴇᴧя {username}...</blockquote>"
            
            if can_edit:
                message = await event.edit(waiting_message, parse_mode="html")
            else:
                message = await event.respond(waiting_message, parse_mode="html")

            stats = await get_message_stats(chat_id, user.id, is_private=is_private)
            
            result = f"<blockquote>⚝ ᴄᴛᴀᴛиᴄᴛиᴋᴀ {username} ʙ {chat_title}</blockquote>\n\n" \
                    f"<blockquote>⚝ ʙᴄᴇᴦо ᴄообщᴇний: <code>{stats['total_messages']}</code>\n" \
                    f"⚝ ʙᴄᴇᴦо ʍᴇдиᴀᴋонᴛᴇнᴛᴀ: <code>{stats['total_media']}</code>\n" \
                    f"⚝ ᴄᴛиᴋᴇᴩоʙ: <code>{stats['stickers']}</code>\n" \
                    f"⚝ GIF: <code>{stats['gifs']}</code>\n" \
                    f"⚝ фоᴛо: <code>{stats['photos']}</code>\n" \
                    f"⚝ ʙидᴇо: <code>{stats['videos']}</code>\n" \
                    f"⚝ ᴦоᴧоᴄоʙых: <code>{stats['voice']}</code>\n" \
                    f"⚝ фᴀйᴧоʙ: <code>{stats['documents']}</code></blockquote>"
            
            if can_edit:
                await message.edit(result, parse_mode="html")
            else:
                await message.respond(result, parse_mode="html")
                
        except Exception as e:
            logger.error(f"Error in usermsg_handler: {e}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if event.out:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")

    @client.on(events.NewMessage(pattern=r'\.allmsg'))
    async def allmsg_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            
            chat_id = event.chat_id
            chat = await client.get_entity(chat_id)
            chat_title = getattr(chat, 'title', None) or "этом канале"

            waiting_message = f"<blockquote>⚝ нᴀчинᴀю ᴨодᴄчᴇᴛ ᴄообщᴇний ʙᴄᴇх учᴀᴄᴛниᴋоʙ ʙ {chat_title}...\nЭᴛо ʍожᴇᴛ зᴀняᴛь нᴇᴋоᴛоᴩоᴇ ʙᴩᴇʍя</blockquote>"
            
            if can_edit:
                message = await event.edit(waiting_message, parse_mode="html")
            else:
                message = await event.respond(waiting_message, parse_mode="html")

            participants = await get_chat_participants(chat_id)

            if not participants:
                error_message = "<blockquote>⚝ нᴇ удᴀᴧоᴄь ᴨоᴧучиᴛь учᴀᴄᴛниᴋоʙ чᴀᴛᴀ</blockquote>"
                if can_edit:
                    await message.edit(error_message, parse_mode="html")
                else:
                    await message.respond(error_message, parse_mode="html")
                return

            users_message_count = []
            
            for user in participants[:50]:  
                if user.deleted:
                    continue
                    
                username = f"@{user.username}" if user.username else f"{user.first_name}"

                try:
                    messages = await client(functions.messages.SearchRequest(
                        peer=chat_id,
                        q="",
                        filter=types.InputMessagesFilterEmpty(),
                        min_date=None,
                        max_date=None,
                        offset_id=0,
                        add_offset=0,
                        limit=0,
                        max_id=0,
                        min_id=0,
                        from_id=user.id,
                        hash=0
                    ))
                    message_count = getattr(messages, 'count', 0)
                    if message_count == 0 and hasattr(messages, 'messages'):
                        message_count = len(messages.messages)
                except Exception:
                    message_count = 0

                if message_count > 0: 
                    users_message_count.append((username, message_count))

            users_message_count.sort(key=lambda x: x[1], reverse=True)

            result = f"<blockquote>⚝ ᴄᴛᴀᴛиᴄᴛиᴋᴀ ᴄообщᴇний ʙ {chat_title}</blockquote>\n\n<blockquote>"
            for username, count in users_message_count:
                result += f"⚝ {username}: <code>{count}</code> ᴄообщᴇний\n"
            result += "</blockquote>"

            if can_edit:
                await message.edit(result, parse_mode="html")
            else:
                await message.respond(result, parse_mode="html")
                
        except Exception as e:
            logger.error(f"Error in allmsg_handler: {e}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if event.out:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")

    @client.on(events.NewMessage(pattern=r'\.chatstats'))
    async def chatstats_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            
            chat_id = event.chat_id
            chat = await client.get_entity(chat_id)
            chat_title = getattr(chat, 'title', None) or "этом канале"

            waiting_message = f"<blockquote>⚝ ᴄобиᴩᴀю ᴄᴛᴀᴛиᴄᴛиᴋу чᴀᴛᴀ {chat_title}...</blockquote>"
            
            if can_edit:
                message = await event.edit(waiting_message, parse_mode="html")
            else:
                message = await event.respond(waiting_message, parse_mode="html")

            stats = await get_chat_total_stats(chat_id)
            
            result = f"<blockquote>⚝ ᴄᴛᴀᴛиᴄᴛиᴋᴀ чᴀᴛᴀ {chat_title}</blockquote>\n\n" \
                    f"<blockquote>⚝ учᴀᴄᴛниᴋоʙ: <code>{stats['total_members']}</code>\n" \
                    f"⚝ ᴀдʍиниᴄᴛᴩᴀᴛоᴩоʙ: <code>{stats['admins']}</code>\n" \
                    f"⚝ удᴀᴧᴇнных ᴀᴋᴋᴀунᴛоʙ: <code>{stats['deleted_accounts']}</code>\n\n" \
                    f"⚝ ʙᴄᴇᴦо ᴄообщᴇний: <code>{stats['total_messages']}</code>\n" \
                    f"⚝ ʍᴇдиᴀ ᴄообщᴇний: <code>{stats['media_messages']}</code></blockquote>"

            if can_edit:
                await message.edit(result, parse_mode="html")
            else:
                await message.respond(result, parse_mode="html")
                
        except Exception as e:
            logger.error(f"Error in chatstats_handler: {e}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if event.out:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")

    @client.on(events.NewMessage(pattern=r'\.silent'))
    async def silent_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            
            chat_id = event.chat_id
            chat = await client.get_entity(chat_id)
            chat_title = getattr(chat, 'title', None) or "этом канале"

            waiting_message = f"<blockquote>⚝ ищу ʍоᴧчуноʙ ʙ {chat_title}...</blockquote>"
            
            if can_edit:
                message = await event.edit(waiting_message, parse_mode="html")
            else:
                message = await event.respond(waiting_message, parse_mode="html")
                
            participants = await client.get_participants(chat_id, limit=100)

            silent_users = []
            
            for user in participants:
                if user.deleted:
                    continue
                
                username = f"@{user.username}" if user.username else f"{user.first_name}"

                try:
                    messages = await client(functions.messages.SearchRequest(
                        peer=chat_id,
                        q="",
                        filter=types.InputMessagesFilterEmpty(),
                        min_date=None,
                        max_date=None,
                        offset_id=0,
                        add_offset=0,
                        limit=1,
                        max_id=0,
                        min_id=0,
                        from_id=user.id,
                        hash=0
                    ))
                    
                    message_count = getattr(messages, 'count', 0)
                    if message_count == 0 and hasattr(messages, 'messages'):
                        message_count = len(messages.messages)
                    
                    if message_count == 0:
                        silent_users.append(username)
                except Exception:
                    continue

            if silent_users:
                result = f"<blockquote>⚝ ʍоᴧчуны ʙ {chat_title}</blockquote>\n\n<blockquote>"
                for user in silent_users:
                    result += f"⚝ {user}\n"
                result += f"\n⚝ ʙᴄᴇᴦо ʍоᴧчуноʙ: <code>{len(silent_users)}</code></blockquote>"
            else:
                result = f"<blockquote>⚝ нᴇᴛ ʍоᴧчуноʙ ʙ {chat_title}!</blockquote>"

            if can_edit:
                await message.edit(result, parse_mode="html")
            else:
                await message.respond(result, parse_mode="html")
                
        except Exception as e:
            logger.error(f"Error in silent_handler: {e}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if event.out:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")
                
    return [mymsg_handler, usermsg_handler, allmsg_handler, chatstats_handler, silent_handler] 