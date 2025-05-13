# meta developer: @nalinormods
# description: Удаляет сообщения от выбранных пользователей
# command: .swmute - `Добавить пользователя в список swmute`
# command: .swunmute - `Удалить пользователя из списка swmute`
# command: .swmutelist - `Получить пользователей в списке swmute`
# command: .swmuteclear - `Удалить всех пользователей из списка swmute`

import logging
import re
import time
import json
from telethon import events, types, functions
from userbot import client, is_owner

logger = logging.getLogger(__name__)

USER_ID_RE = re.compile(r"^(-100)?\d+$")

def s2time(string) -> int:
    """Parse time from text string"""
    r = {} 

    for time_type in ["mon", "w", "d", "h", "m", "s"]:
        try:
            r[time_type] = int(re.search(rf"(\d+)\s*{time_type}", string)[1])
        except TypeError:
            r[time_type] = 0

    return (
        r["mon"] * 86400 * 30
        + r["w"] * 86400 * 7
        + r["d"] * 86400
        + r["h"] * 3600
        + r["m"] * 60
        + r["s"]
    )

def get_link(user) -> str:
    """Return permanent link to user"""
    try:
        name = user.first_name if hasattr(user, "first_name") else user.title
        return f"<a href='tg://user?id={user.id}'>{name}</a>"
    except:
        return f"<code>{user.id}</code>"

def plural_number(n: int) -> str:
    """Pluralize number n"""
    return (
        "one" if n % 10 == 1 and n % 100 != 11
        else "few" if 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20)
        else "many"
    )

def register_handlers(client):
    strings = {
        "not_group": "<blockquote>⚝ эᴛᴀ ᴋоʍᴀндᴀ ᴨᴩᴇднᴀзнᴀчᴇнᴀ ᴛоᴧьᴋо дᴧя ᴦᴩуᴨᴨ</blockquote>",
        "muted": "<blockquote>⚝ ᴨоᴧьзоʙᴀᴛᴇᴧь {user} добᴀʙᴧᴇн ʙ ᴄᴨиᴄоᴋ swmute нᴀ {time}</blockquote>",
        "muted_forever": "<blockquote>⚝ ᴨоᴧьзоʙᴀᴛᴇᴧь {user} добᴀʙᴧᴇн ʙ ᴄᴨиᴄоᴋ swmute нᴀʙᴄᴇᴦдᴀ</blockquote>",
        "unmuted": "<blockquote>⚝ ᴨоᴧьзоʙᴀᴛᴇᴧь {user} удᴀᴧён из ᴄᴨиᴄᴋᴀ swmute</blockquote>",
        "not_muted": "<blockquote>⚝ эᴛоᴛ ᴨоᴧьзоʙᴀᴛᴇᴧь нᴇ быᴧ ʙ ʍуᴛᴇ</blockquote>",
        "no_mute_target": "<blockquote>⚝ уᴋᴀжиᴛᴇ ᴨоᴧьзоʙᴀᴛᴇᴧя дᴧя ᴄʙʍуᴛᴀ</blockquote>",
        "no_unmute_target": "<blockquote>⚝ уᴋᴀжиᴛᴇ ᴨоᴧьзоʙᴀᴛᴇᴧя дᴧя ᴄняᴛия ᴄʙʍуᴛᴀ</blockquote>",
        "mutes_empty": "<blockquote>⚝ ʙ эᴛой ᴦᴩуᴨᴨᴇ ниᴋᴛо нᴇ ʙ ʍуᴛᴇ</blockquote>",
        "muted_users": "<blockquote>⚝ ᴨоᴧьзоʙᴀᴛᴇᴧи ʙ ᴄᴨиᴄᴋᴇ swmute:</blockquote>\n\n<blockquote>{names}</blockquote>",
        "cleared": "<blockquote>⚝ ᴄᴨиᴄоᴋ ʍуᴛоʙ ʙ эᴛой ᴦᴩуᴨᴨᴇ очищᴇн</blockquote>",
        "cleared_all": "<blockquote>⚝ ʙᴄᴇ ᴄᴨиᴄᴋи ʍуᴛоʙ очищᴇны</blockquote>",
        "s_one": "ᴄᴇᴋундᴀ",
        "s_few": "ᴄᴇᴋунды",
        "s_many": "ᴄᴇᴋунд",
        "m_one": "ʍинуᴛᴀ",
        "m_few": "ʍинуᴛы",
        "m_many": "ʍинуᴛ",
        "h_one": "чᴀᴄ",
        "h_few": "чᴀᴄᴀ",
        "h_many": "чᴀᴄоʙ",
        "d_one": "дᴇнь",
        "d_few": "дня",
        "d_many": "днᴇй",
    }
    
    def format_time(seconds: int, max_words: int = None) -> str:
        """Format time to human-readable variant"""
        words = []
        time_dict = {
            "d": seconds // 86400,
            "h": seconds % 86400 // 3600,
            "m": seconds % 3600 // 60,
            "s": seconds % 60,
        }

        for time_type, count in time_dict.items():
            if max_words and len(words) >= max_words:
                break

            if count != 0:
                words.append(
                    f"{count} {strings[time_type + '_' + plural_number(count)]}"
                )

        return " ".join(words)
    
    def get_mutes():
        try:
            with open("data/swmute.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
            
    def save_mutes(mutes):
        import os
        if not os.path.exists("data"):
            os.makedirs("data")
        with open("data/swmute.json", "w", encoding="utf-8") as f:
            json.dump(mutes, f)
    
    def mute(chat_id: int, user_id: int, until_time: int = 0):
        """Add user to mute list"""
        chat_id = str(chat_id)
        user_id = str(user_id)
        
        mutes = get_mutes()
        mutes.setdefault(chat_id, {})
        mutes[chat_id][user_id] = until_time
        save_mutes(mutes)
        
        logger.debug(f"Muted user {user_id} in chat {chat_id}")
    
    def unmute(chat_id: int, user_id: int):
        """Remove user from mute list"""
        chat_id = str(chat_id)
        user_id = str(user_id)
        
        mutes = get_mutes()
        if chat_id in mutes and user_id in mutes[chat_id]:
            mutes[chat_id].pop(user_id)
        save_mutes(mutes)
        
        logger.debug(f"Unmuted user {user_id} in chat {chat_id}")
    
    def get_muted_users(chat_id: int):
        """Get current mutes for specified chat"""
        return [
            int(user_id)
            for user_id, until_time in get_mutes().get(str(chat_id), {}).items()
            if until_time > time.time() or until_time == 0
        ]
    
    def get_mute_time(chat_id: int, user_id: int) -> int:
        """Get mute expiration timestamp"""
        return get_mutes().get(str(chat_id), {}).get(str(user_id))
    
    def cleanup():
        """Cleanup expired mutes"""
        mutes = {}
        
        for chat_id, chat_mutes in get_mutes().items():
            if new_chat_mutes := {
                user_id: until_time
                for user_id, until_time in chat_mutes.items()
                if until_time == 0 or until_time > time.time()
            }:
                mutes[chat_id] = new_chat_mutes
        
        save_mutes(mutes)
    
    def clear_mutes(chat_id: int = None):
        """Clear all mutes for given or all chats"""
        if chat_id:
            mutes = get_mutes()
            mutes.pop(str(chat_id), None)
            save_mutes(mutes)
        else:
            save_mutes({})
    
    @client.on(events.NewMessage(pattern=r'\.swmute(?:\s+(.+))?'))
    async def swmute_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            
            if not event.is_group:
                if can_edit:
                    await event.edit(strings["not_group"], parse_mode="html")
                else:
                    await event.respond(strings["not_group"], parse_mode="html")
                return
            
            args = event.message.message.split(maxsplit=1)[1].split() if len(event.message.message.split()) > 1 else []
            reply = await event.get_reply_message()
            
            if reply and reply.sender_id:
                user_id = reply.sender_id
                try:
                    user = await client.get_entity(reply.sender_id)
                except Exception:
                    user = types.PeerUser(user_id)
                string_time = " ".join(args) if args else False
            elif args:
                try:
                    user = await client.get_entity(
                        int(args[0]) if USER_ID_RE.match(args[0]) else args[0]
                    )
                    user_id = user.id
                    string_time = " ".join(args[1:]) if len(args) > 1 else False
                except ValueError:
                    if can_edit:
                        await event.edit(strings["no_mute_target"], parse_mode="html")
                    else:
                        await event.respond(strings["no_mute_target"], parse_mode="html")
                    return
            else:
                if can_edit:
                    await event.edit(strings["no_mute_target"], parse_mode="html")
                else:
                    await event.respond(strings["no_mute_target"], parse_mode="html")
                return
            
            cleanup()
            
            if string_time:
                if mute_seconds := s2time(string_time):
                    mute(event.chat_id, user_id, int(time.time() + mute_seconds))
                    result = strings["muted"].format(
                        time=format_time(mute_seconds), 
                        user=get_link(user)
                    )
                    if can_edit:
                        await event.edit(result, parse_mode="html")
                    else:
                        await event.respond(result, parse_mode="html")
                    return
            
            mute(event.chat_id, user_id)
            result = strings["muted_forever"].format(user=get_link(user))
            if can_edit:
                await event.edit(result, parse_mode="html")
            else:
                await event.respond(result, parse_mode="html")
        except Exception as e:
            logger.error(f"Error in swmute_handler: {e}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if can_edit:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")
    
    @client.on(events.NewMessage(pattern=r'\.swunmute(?:\s+(.+))?'))
    async def swunmute_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            
            if not event.is_group:
                if can_edit:
                    await event.edit(strings["not_group"], parse_mode="html")
                else:
                    await event.respond(strings["not_group"], parse_mode="html")
                return
            
            args = event.message.message.split(maxsplit=1)[1].split() if len(event.message.message.split()) > 1 else []
            reply = await event.get_reply_message()
            
            if reply and reply.sender_id:
                user_id = reply.sender_id
                try:
                    user = await client.get_entity(reply.sender_id)
                except Exception:
                    user = types.PeerUser(user_id)
            elif args:
                try:
                    user = await client.get_entity(
                        int(args[0]) if USER_ID_RE.match(args[0]) else args[0]
                    )
                    user_id = user.id
                except ValueError:
                    if can_edit:
                        await event.edit(strings["no_unmute_target"], parse_mode="html")
                    else:
                        await event.respond(strings["no_unmute_target"], parse_mode="html")
                    return
            else:
                if can_edit:
                    await event.edit(strings["no_unmute_target"], parse_mode="html")
                else:
                    await event.respond(strings["no_unmute_target"], parse_mode="html")
                return
            
            unmute(event.chat_id, user_id)
            result = strings["unmuted"].format(user=get_link(user))
            if can_edit:
                await event.edit(result, parse_mode="html")
            else:
                await event.respond(result, parse_mode="html")
        except Exception as e:
            logger.error(f"Error in swunmute_handler: {e}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if can_edit:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")
    
    @client.on(events.NewMessage(pattern=r'\.swmutelist'))
    async def swmutelist_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            
            if not event.is_group:
                if can_edit:
                    await event.edit(strings["not_group"], parse_mode="html")
                else:
                    await event.respond(strings["not_group"], parse_mode="html")
                return
            
            cleanup()
            
            mutes = get_muted_users(event.chat_id)
            if not mutes:
                if can_edit:
                    await event.edit(strings["mutes_empty"], parse_mode="html")
                else:
                    await event.respond(strings["mutes_empty"], parse_mode="html")
                return
            
            muted_users = []
            for mute_id in mutes:
                text = "⚝ "
                
                try:
                    user = await client.get_entity(mute_id)
                    text += f"{get_link(user)}"
                except ValueError:
                    text += f"<code>{mute_id}</code>"
                
                if until_ts := get_mute_time(event.chat_id, mute_id):
                    if until_ts > 0:  
                        time_left = int(until_ts - time.time())
                        if time_left > 0:
                            time_formatted = format_time(time_left, max_words=2)
                            text += f" - оᴄᴛᴀᴧоᴄь {time_formatted}"
                
                muted_users.append(text)
            
            result = strings["muted_users"].format(names="\n".join(muted_users))
            if can_edit:
                await event.edit(result, parse_mode="html")
            else:
                await event.respond(result, parse_mode="html")
        except Exception as e:
            logger.error(f"Error in swmutelist_handler: {e}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if can_edit:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")
    
    @client.on(events.NewMessage(pattern=r'\.swmuteclear(?:\s+(.+))?'))
    async def swmuteclear_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            
            if not event.is_group:
                if can_edit:
                    await event.edit(strings["not_group"], parse_mode="html")
                else:
                    await event.respond(strings["not_group"], parse_mode="html")
                return
            
            args = event.message.message.split(maxsplit=1)[1] if len(event.message.message.split()) > 1 else ""
            
            if "all" in args:
                clear_mutes()
                if can_edit:
                    await event.edit(strings["cleared_all"], parse_mode="html")
                else:
                    await event.respond(strings["cleared_all"], parse_mode="html")
            else:
                clear_mutes(event.chat_id)
                if can_edit:
                    await event.edit(strings["cleared"], parse_mode="html")
                else:
                    await event.respond(strings["cleared"], parse_mode="html")
        except Exception as e:
            logger.error(f"Error in swmuteclear_handler: {e}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if can_edit:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")
    
    @client.on(events.NewMessage)
    async def swmute_watcher(event):
        try:
            if not event.is_group or event.out:
                return
                
            if event.sender_id in get_muted_users(event.chat_id):
                await event.delete()
                logger.debug(f"Deleted message from user {event.sender_id} in chat {event.chat_id}")
        except Exception as e:
            logger.error(f"Error in swmute_watcher: {e}")
    
    cleanup()
    
    return [swmute_handler, swunmute_handler, swmutelist_handler, swmuteclear_handler, swmute_watcher] 