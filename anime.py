# meta developer: @aki_modules
# description: Получение случайных аниме-картинок из API nekosia.cat или nekos.life
# command: .rapic - `Получить случайную аниме-картинку`

import requests
import asyncio
import random
import logging
from telethon import events
from telethon.errors import MessageIdInvalidError
from userbot import client, is_owner

logger = logging.getLogger(__name__)

ANIME_APIS = [
    {"url": "https://api.nekosia.cat/api/v1/images/cute?count=1", "parser": lambda data: data['image']['original']['url']},
    {"url": "https://nekos.life/api/v2/img/neko", "parser": lambda data: data['url']},
    {"url": "https://api.waifu.pics/sfw/neko", "parser": lambda data: data['url']}
]

def register_handlers(client):
    @client.on(events.NewMessage(pattern=r'\.rapic'))
    async def anime_pic_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return  
                
            can_edit = event.out
            
            try:
                if can_edit:
                    loading_msg = await event.edit("<blockquote>⚝ зᴀᴦᴩузᴋᴀ изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
                else:
                    loading_msg = await event.respond("<blockquote>⚝ зᴀᴦᴩузᴋᴀ изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
            except Exception as e:
                logger.warning(f"Failed to edit/send loading message: {str(e)}")
                loading_msg = await event.respond("<blockquote>⚝ зᴀᴦᴩузᴋᴀ изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
                can_edit = False
            
            apis = ANIME_APIS.copy()
            random.shuffle(apis)
            
            image_url = None
            error_messages = []
            
            for api in apis:
                try:
                    response = requests.get(api["url"], timeout=5)
                    response.raise_for_status()
                    data = response.json()
                    image_url = api["parser"](data)
                    break
                except Exception as e:
                    error_messages.append(f"{api['url']}: {str(e)}")
                    continue
            
            if not image_url:
                raise Exception(f"ʙᴄᴇ ᴀᴘɪ нᴇдоᴄᴛуᴨны: {', '.join(error_messages)}")
            
            await asyncio.sleep(0.5)
            
            reply_to = event.reply_to_msg_id if event.is_reply else None
            await client.send_file(
                event.chat_id, 
                image_url, 
                caption=f"<blockquote>⚝ ᴀниʍᴇ ᴋᴀᴩᴛинᴋᴀ</blockquote>\n<blockquote>⚝ ᴄᴄыᴧᴋᴀ: {image_url}</blockquote>",
                reply_to=reply_to,
                parse_mode="html"
            )
            
            try:
                await loading_msg.delete()
            except Exception as e:
                logger.debug(f"Failed to delete loading message: {str(e)}")
            
        except Exception as e:
            try:
                error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
                
                if isinstance(loading_msg, (events.NewMessage.Event, events.MessageEdited.Event)):
                    can_edit = loading_msg.out
                
                if can_edit:
                    try:
                        error_msg = await event.edit(error_message, parse_mode="html")
                    except MessageIdInvalidError:
                        error_msg = await event.respond(error_message, parse_mode="html")
                    except Exception:
                        error_msg = await event.respond(error_message, parse_mode="html")
                else:
                    error_msg = await event.respond(error_message, parse_mode="html")
                
                await asyncio.sleep(5)
                try:
                    await error_msg.delete()
                except Exception:
                    pass
            except Exception as err:
                logger.error(f"Failed to handle error in anime_pic_handler: {str(err)}")
    
    return anime_pic_handler 