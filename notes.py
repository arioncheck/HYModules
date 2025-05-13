# meta developer: @hikarimods
# description: Модуль заметок с расширенным функционалом. Папки и категории
# command: .hsave [папка] <имя> - `Сохранить заметку`
# command: .hget [имя] - `Показать заметку`
# command: .hdel [имя] - `Удалить заметку`
# command: .hlist [папка] - `Показать все заметки`

import logging
from telethon.tl.types import Message
from telethon import events
from userbot import client, is_owner
import json
import os

logger = logging.getLogger(__name__)

def register_handlers(client):
    """
    Модуль заметок с расширенным функционалом. Папки и категории
    """

    if not os.path.exists('data'):
        os.makedirs('data')

    def get_notes():
        try:
            with open('data/notes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_notes(notes):
        with open('data/notes.json', 'w', encoding='utf-8') as f:
            json.dump(notes, f, ensure_ascii=False, indent=4)

    def get_owner_id():
        if hasattr(client, '_owner_id'):
            return client._owner_id

        try:
            from dotenv import load_dotenv
            load_dotenv()
            env_owner_id = os.getenv('OWNER_ID')
            if env_owner_id and env_owner_id.isdigit():
                client._owner_id = int(env_owner_id)
                return client._owner_id
        except Exception:
            pass
            
        return None

    notes_db = get_notes()

    if not os.path.exists('data/assets'):
        os.makedirs('data/assets')

    async def store_asset(message):
        asset_id = f"{message.chat_id}_{message.id}"
        asset_data = {
            "chat_id": message.chat_id,
            "message_id": message.id,
            "date": message.date.timestamp() if message.date else 0,
        }
        
        with open(f'data/assets/{asset_id}.json', 'w', encoding='utf-8') as f:
            json.dump(asset_data, f)
        
        return asset_id

    async def fetch_asset(asset_id):
        try:
            with open(f'data/assets/{asset_id}.json', 'r', encoding='utf-8') as f:
                asset_data = json.load(f)
            
            return await client.get_messages(
                asset_data["chat_id"],
                ids=asset_data["message_id"]
            )
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            logger.error(f"Error fetching asset {asset_id}: {e}")
            return None
    
    @client.on(events.NewMessage(pattern=r'\.hsave'))
    async def hsave_handler(event):
        """[папка] <имя> - Сохранить заметку"""
        try:
            sender_id = event.sender_id
            
            if not hasattr(client, '_owner_id'):
                owner_id = get_owner_id()
                if not owner_id:
                    me = await client.get_me()
                    client._owner_id = me.id
                    
                    try:
                        from dotenv import load_dotenv, set_key
                        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
                        load_dotenv(dotenv_path)
                        set_key(dotenv_path, "OWNER_ID", str(client._owner_id))
                    except Exception:
                        pass
 
            is_owner_msg = (sender_id == client._owner_id)
            is_self_msg = event.out

            if not (is_owner_msg or is_self_msg):
                return  

            args = event.text.split(' ', 1)
            if len(args) < 2:
                await event.edit("<blockquote>уᴋᴀжи иʍя зᴀʍᴇᴛᴋи.</blockquote>", parse_mode="html")
                return
            
            args = args[1]
            
            if len(args.split()) >= 2:
                folder = args.split()[0]
                args = args.split(maxsplit=1)[1]
            else:
                folder = "global"
            
            reply = await event.get_reply_message()
            
            if not (reply and args):
                await event.edit("<blockquote>ᴛᴩᴇбуᴇᴛᴄя ᴩᴇᴨᴧᴀй нᴀ ᴋонᴛᴇнᴛ зᴀʍᴇᴛᴋи.</blockquote>", parse_mode="html")
                return
            
            if folder not in notes_db:
                notes_db[folder] = {}
                logger.warning(f"Created new folder {folder}")
            
            asset = await store_asset(reply)
            
            if getattr(reply, "video", False):
                type_ = "⚝"
            elif getattr(reply, "photo", False):
                type_ = "⚝"
            elif getattr(reply, "voice", False):
                type_ = "⚝"
            elif getattr(reply, "audio", False):
                type_ = "⚝"
            elif getattr(reply, "file", False):
                type_ = "⚝"
            else:
                type_ = "⚝"
            
            notes_db[folder][args] = {"id": asset, "type": type_}
            
            save_notes(notes_db)
            
            await event.edit(f"<blockquote>зᴀʍᴇᴛᴋᴀ ᴄ иʍᴇнᴇʍ <code>{args}</code> ᴄохᴩᴀнᴇнᴀ.</blockquote>\n<blockquote>ᴨᴀᴨᴋᴀ: <code>{folder}</code>.</blockquote>", parse_mode="html")
        except Exception as e:
            logger.error(f"Error in hsave_handler: {e}")
            await event.edit("<blockquote>ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ ᴨᴩи ᴄохᴩᴀнᴇнии зᴀʍᴇᴛᴋи.</blockquote>", parse_mode="html")
    
    def get_note(name):
        for category, notes in notes_db.items():
            for note, asset in notes.items():
                if note == name:
                    return asset
        return None
    
    def del_note(name):
        for category, notes in notes_db.copy().items():
            for note, asset in notes.copy().items():
                if note == name:
                    del notes_db[category][note]
                    
                    if not notes_db[category]:
                        del notes_db[category]
                    
                    save_notes(notes_db)
                    return True
        
        return False
    
    @client.on(events.NewMessage(pattern=r'\.hget'))
    async def hget_handler(event):
        """<имя> - Показать заметку"""
        try:
            sender_id = event.sender_id
            
            if not hasattr(client, '_owner_id'):
                owner_id = get_owner_id()
                if not owner_id:
                    me = await client.get_me()
                    client._owner_id = me.id
                    
                    try:
                        from dotenv import load_dotenv, set_key
                        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
                        load_dotenv(dotenv_path)
                        set_key(dotenv_path, "OWNER_ID", str(client._owner_id))
                    except Exception:
                        pass
            
            is_owner_msg = (sender_id == client._owner_id)
            is_self_msg = event.out
            
            if not (is_owner_msg or is_self_msg):
                return  
            
            args = event.text.split(' ', 1)
            if len(args) < 2:
                await event.edit("<blockquote>уᴋᴀжи иʍя зᴀʍᴇᴛᴋи.</blockquote>", parse_mode="html")
                return
            
            args = args[1]
            
            asset = get_note(args)
            if not asset:
                await event.edit("<blockquote>зᴀʍᴇᴛᴋᴀ нᴇ нᴀйдᴇнᴀ.</blockquote>", parse_mode="html")
                return
            
            message = await fetch_asset(asset["id"])
            if not message:
                await event.edit("<blockquote>нᴇ удᴀᴧоᴄь ᴨоᴧучиᴛь зᴀʍᴇᴛᴋу.</blockquote>", parse_mode="html")
                return
            
            await client.send_message(
                event.chat_id,
                message,
                reply_to=event.reply_to_msg_id if event.reply_to_msg_id else None,
            )
            
            if event.out:
                await event.delete()
        except Exception as e:
            logger.error(f"Error in hget_handler: {str(e)}")
            await event.edit("<blockquote>ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ ᴨᴩи ᴨоᴧучᴇнии зᴀʍᴇᴛᴋи.</blockquote>", parse_mode="html")
    
    @client.on(events.NewMessage(pattern=r'\.hdel'))
    async def hdel_handler(event):
        """<имя> - Удалить заметку"""
        try:
            sender_id = event.sender_id
            
            if not hasattr(client, '_owner_id'):
                owner_id = get_owner_id()
                if not owner_id:
                    me = await client.get_me()
                    client._owner_id = me.id
                    
                    try:
                        from dotenv import load_dotenv, set_key
                        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
                        load_dotenv(dotenv_path)
                        set_key(dotenv_path, "OWNER_ID", str(client._owner_id))
                    except Exception:
                        pass
            
            is_owner_msg = (sender_id == client._owner_id)
            is_self_msg = event.out
            
            if not (is_owner_msg or is_self_msg):
                return  
            
            args = event.text.split(' ', 1)
            if len(args) < 2:
                await event.edit("<blockquote>уᴋᴀжи иʍя зᴀʍᴇᴛᴋи.</blockquote>", parse_mode="html")
                return
            
            args = args[1]
            
            asset = get_note(args)
            if not asset:
                await event.edit("<blockquote>зᴀʍᴇᴛᴋᴀ нᴇ нᴀйдᴇнᴀ.</blockquote>", parse_mode="html")
                return
            
            try:
                if os.path.exists(f'data/assets/{asset["id"]}.json'):
                    os.remove(f'data/assets/{asset["id"]}.json')
            except Exception:
                pass
            
            del_note(args)
            
            await event.edit(f"<blockquote>зᴀʍᴇᴛᴋᴀ ᴄ иʍᴇнᴇʍ <code>{args}</code> удᴀᴧᴇнᴀ</blockquote>", parse_mode="html")
        except Exception as e:
            logger.error(f"Error in hdel_handler: {e}")
            await event.edit("<blockquote>ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ ᴨᴩи удᴀᴧᴇнии зᴀʍᴇᴛᴋи.</blockquote>", parse_mode="html")
    
    @client.on(events.NewMessage(pattern=r'\.hlist'))
    async def hlist_handler(event):
        """[папка] - Показать все заметки"""
        try:
            sender_id = event.sender_id
            
            if not hasattr(client, '_owner_id'):
                owner_id = get_owner_id()
                if not owner_id:
                    me = await client.get_me()
                    client._owner_id = me.id
                    
                    try:
                        from dotenv import load_dotenv, set_key
                        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
                        load_dotenv(dotenv_path)
                        set_key(dotenv_path, "OWNER_ID", str(client._owner_id))
                    except Exception:
                        pass
            
            is_owner_msg = (sender_id == client._owner_id)
            is_self_msg = event.out
            
            if not (is_owner_msg or is_self_msg):
                return 
            
            args = event.text.split(' ', 1)
            args = args[1] if len(args) > 1 else ""
            
            if not notes_db:
                await event.edit("<blockquote>у ᴛᴇбя ᴨоᴋᴀ чᴛо нᴇᴛ зᴀʍᴇᴛоᴋ</blockquote>", parse_mode="html")
                return
            
            result = "<blockquote>ᴛᴇᴋущиᴇ зᴀʍᴇᴛᴋи:</blockquote>\n"
            
            if not args or args not in notes_db:
                for category, notes in notes_db.items():
                    result += f"\n<blockquote>⚝ <b>{category}</b></blockquote>\n"
                    for note, asset in notes.items():
                        result += f"<blockquote>    {asset['type']} <code>{note}</code></blockquote>\n"
            
                await event.edit(result, parse_mode="html")
                return
            
            for note, asset in notes_db[args].items():
                result += f"<blockquote>{asset['type']} <code>{note}</code></blockquote>\n"
            
            await event.edit(result, parse_mode="html")
        except Exception as e:
            logger.error(f"Error in hlist_handler: {e}")
            await event.edit("<blockquote>ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ ᴨᴩи ᴨоᴧучᴇнии ᴄᴨиᴄᴋᴀ зᴀʍᴇᴛоᴋ.</blockquote>", parse_mode="html")
    
    return [hsave_handler, hget_handler, hdel_handler, hlist_handler] 
