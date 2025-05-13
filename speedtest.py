# meta developer: @codrago_m
# description: Тест скорости интернет-соединения
# command: .speedtest - `Запуск теста скорости интернет-соединения`

import speedtest
import logging
import time
from telethon import events
from userbot import client, is_owner

logger = logging.getLogger(__name__)

def register_handlers(client):
    @client.on(events.NewMessage(pattern=r'\.speedtest'))
    async def speedtest_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            
            running_message = "<blockquote>⚝ зᴀᴨуᴄᴋ ᴛᴇᴄᴛᴀ ᴄᴋоᴩоᴄᴛи...</blockquote>"
            
            if can_edit:
                message = await event.edit(running_message, parse_mode="html")
            else:
                message = await event.respond(running_message, parse_mode="html")
            
            try:
                st = speedtest.Speedtest()
                st.download()
                st.upload()
                results = st.results.dict()
                
                download = round(results["download"] / 1_000_000, 2)  
                upload = round(results["upload"] / 1_000_000, 2)  
                ping = round(results["ping"], 2)
                
                result_message = f"<blockquote>⚝ ᴩᴇзуᴧьᴛᴀᴛы ᴛᴇᴄᴛᴀ ᴄᴋоᴩоᴄᴛи</blockquote>\n\n" \
                                f"<blockquote>⚝ ᴄᴋᴀчиʙᴀниᴇ: <code>{download} Мбиᴛ/ᴄ</code>\n" \
                                f"⚝ зᴀᴦᴩузᴋᴀ: <code>{upload} Мбиᴛ/ᴄ</code>\n" \
                                f"⚝ ᴨинᴦ: <code>{ping} ʍᴄ</code></blockquote>"
                
                if can_edit:
                    await message.edit(result_message, parse_mode="html")
                else:
                    await message.respond(result_message, parse_mode="html")
                    
            except Exception as e:
                error_message = f"<blockquote>⚝ оɯибᴋᴀ ᴨᴩи зᴀᴨуᴄᴋᴇ ᴛᴇᴄᴛᴀ ᴄᴋоᴩоᴄᴛи: {str(e)}</blockquote>"
                if can_edit:
                    await message.edit(error_message, parse_mode="html")
                else:
                    await message.respond(error_message, parse_mode="html")
                    
        except Exception as e:
            logger.error(f"Ошибка в speedtest_handler: {str(e)}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if event.out:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")
    
    return [speedtest_handler] 