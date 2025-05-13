# meta developer: @codrago_m
# description: Получение случайных хентай-изображений
# command: .loli - `Получить случайное лоли изображение`
# command: .fem - `Получить случайное фембой изображение`
# command: .sfw - `Получить случайное SFW изображение`
# command: .furry - `Получить случайное фурри изображение`
# command: .nsfw - `Получить случайное NSFW изображение`

import os
import random
import time
import datetime
import asyncio
import logging
from telethon import events, functions
from telethon.errors import MessageIdInvalidError
from userbot import client, is_owner

logger = logging.getLogger(__name__)

def register_handlers(client):
    async def check_owner(event):
        """Более строгая проверка владельца, не полагающаяся на глобальную функцию is_owner"""
        try:
            if not hasattr(client, '_owner_id'):
                try:
                    try:
                        from dotenv import load_dotenv
                        load_dotenv()
                        env_owner_id = os.getenv('OWNER_ID')
                        if env_owner_id and env_owner_id.isdigit():
                            client._owner_id = int(env_owner_id)
                            return event.out or event.sender_id == client._owner_id
                    except Exception:
                        pass
                    
                    me = await client.get_me()
                    client._owner_id = me.id
                    
                    try:
                        from dotenv import load_dotenv, set_key
                        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
                        load_dotenv(dotenv_path)
                        set_key(dotenv_path, "OWNER_ID", str(client._owner_id))
                    except Exception:
                        pass
                        
                except Exception as e:
                    logger.error(f"Failed to get owner ID: {e}")
                    return True
            
            if event.out:
                return True
                
            sender_id = event.sender_id
            is_owner_result = (sender_id == client._owner_id)
            
            
            return is_owner_result
        except Exception as e:
            logger.error(f"Error in check_owner: {e}")
            return True

    @client.on(events.NewMessage(pattern=r'\.loli'))
    async def loli_handler(event):
        try:
            if not await check_owner(event):
                return  
                
            can_edit = event.out
            
            try:
                if can_edit:
                    loading_msg = await event.edit("<blockquote>⚝ зᴀᴦᴩузᴋᴀ ᴧоᴧи изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
                else:
                    loading_msg = await event.respond("<blockquote>⚝ зᴀᴦᴩузᴋᴀ ᴧоᴧи изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
            except Exception as e:
                logger.warning(f"Failed to edit/send loading message: {str(e)}")
                loading_msg = await event.respond("<blockquote>⚝ зᴀᴦᴩузᴋᴀ ᴧоᴧи изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
                can_edit = False
                
            try:
                async with client.conversation("@ferganteusbot") as conv:
                    try: 
                        lh = await conv.send_message("/lh")
                    except Exception as e:
                        error_message = "<blockquote>⚝ оɯибᴋᴀ: нᴇ удᴀᴧоᴄь ᴨоᴧучиᴛь изобᴩᴀжᴇниᴇ. ᴩᴀзбᴧоᴋиᴩуйᴛᴇ @ferganteusbot</blockquote>"
                        
                        try:
                            await loading_msg.edit(error_message, parse_mode="html")
                        except Exception:
                            await event.respond(error_message, parse_mode="html")
                            
                        await asyncio.sleep(5)
                        try:
                            await loading_msg.delete()
                        except Exception:
                            pass
                        return
                    
                    otvet = await conv.get_response()
                    await lh.delete()
                    
                    if otvet.media:
                        reply_to = event.reply_to_msg_id if event.is_reply else None
                        await client.send_file(
                            event.chat_id,
                            otvet.media,
                            caption="<blockquote>⚝ ᴧоᴧи изобᴩᴀжᴇниᴇ</blockquote>",
                            reply_to=reply_to,
                            parse_mode="html"
                        )
                        await otvet.delete()
                        try:
                            await loading_msg.delete()
                        except Exception:
                            pass
                    else:
                        error_message = "<blockquote>⚝ оɯибᴋᴀ: нᴇ удᴀᴧоᴄь ᴨоᴧучиᴛь изобᴩᴀжᴇниᴇ</blockquote>"
                        
                        try:
                            await loading_msg.edit(error_message, parse_mode="html")
                        except Exception:
                            await event.respond(error_message, parse_mode="html")
                            
                        await asyncio.sleep(5)
                        try:
                            await loading_msg.delete()
                        except Exception:
                            pass
            
            except Exception as e:
                error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
                
                try:
                    await loading_msg.edit(error_message, parse_mode="html")
                except Exception:
                    await event.respond(error_message, parse_mode="html")
                    
                await asyncio.sleep(5)
                try:
                    await loading_msg.delete()
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Critical error in loli_handler: {str(e)}")
                
    @client.on(events.NewMessage(pattern=r'\.fem'))
    async def fem_handler(event):
        try:
            if not await check_owner(event):
                return  
                
            can_edit = event.out
            
            try:
                if can_edit:
                    loading_msg = await event.edit("<blockquote>⚝ зᴀᴦᴩузᴋᴀ ɸᴇʍбой изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
                else:
                    loading_msg = await event.respond("<blockquote>⚝ зᴀᴦᴩузᴋᴀ ɸᴇʍбой изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
            except Exception as e:
                logger.warning(f"Failed to edit/send loading message: {str(e)}")
                loading_msg = await event.respond("<blockquote>⚝ зᴀᴦᴩузᴋᴀ ɸᴇʍбой изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
                can_edit = False
                
            try:
                async with client.conversation("@ferganteusbot") as conv:
                    try: 
                        fm = await conv.send_message("/fm")
                    except Exception as e:
                        error_message = "<blockquote>⚝ оɯибᴋᴀ: нᴇ удᴀᴧоᴄь ᴨоᴧучиᴛь изобᴩᴀжᴇниᴇ. ᴩᴀзбᴧоᴋиᴩуйᴛᴇ @ferganteusbot</blockquote>"
                        
                        try:
                            await loading_msg.edit(error_message, parse_mode="html")
                        except Exception:
                            await event.respond(error_message, parse_mode="html")
                            
                        await asyncio.sleep(5)
                        try:
                            await loading_msg.delete()
                        except Exception:
                            pass
                        return
                    
                    response = await conv.get_response()
                    await fm.delete()
                    
                    if response.media:
                        reply_to = event.reply_to_msg_id if event.is_reply else None
                        await client.send_file(
                            event.chat_id,
                            response.media,
                            caption="<blockquote>⚝ ɸᴇʍбой изобᴩᴀжᴇниᴇ</blockquote>",
                            reply_to=reply_to,
                            parse_mode="html"
                        )
                        await response.delete()
                        try:
                            await loading_msg.delete()
                        except Exception:
                            pass
                    else:
                        error_message = "<blockquote>⚝ оɯибᴋᴀ: нᴇ удᴀᴧоᴄь ᴨоᴧучиᴛь изобᴩᴀжᴇниᴇ</blockquote>"
                        
                        try:
                            await loading_msg.edit(error_message, parse_mode="html")
                        except Exception:
                            await event.respond(error_message, parse_mode="html")
                            
                        await asyncio.sleep(5)
                        try:
                            await loading_msg.delete()
                        except Exception:
                            pass
            
            except Exception as e:
                error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
                
                try:
                    await loading_msg.edit(error_message, parse_mode="html")
                except Exception:
                    await event.respond(error_message, parse_mode="html")
                    
                await asyncio.sleep(5)
                try:
                    await loading_msg.delete()
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Critical error in fem_handler: {str(e)}")
    
    @client.on(events.NewMessage(pattern=r'\.sfw'))
    async def sfw_handler(event):
        try:
            if not await check_owner(event):
                return  
                
            can_edit = event.out
            
            try:
                if can_edit:
                    loading_msg = await event.edit("<blockquote>⚝ зᴀᴦᴩузᴋᴀ sꜰᴡ изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
                else:
                    loading_msg = await event.respond("<blockquote>⚝ зᴀᴦᴩузᴋᴀ sꜰᴡ изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
            except Exception as e:
                logger.warning(f"Failed to edit/send loading message: {str(e)}")
                loading_msg = await event.respond("<blockquote>⚝ зᴀᴦᴩузᴋᴀ sꜰᴡ изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
                can_edit = False
                
            try:
                async with client.conversation("@ferganteusbot") as conv:
                    try: 
                        rc = await conv.send_message("/rc")
                    except Exception as e:
                        error_message = "<blockquote>⚝ оɯибᴋᴀ: нᴇ удᴀᴧоᴄь ᴨоᴧучиᴛь изобᴩᴀжᴇниᴇ. ᴩᴀзбᴧоᴋиᴩуйᴛᴇ @ferganteusbot</blockquote>"
                        
                        try:
                            await loading_msg.edit(error_message, parse_mode="html")
                        except Exception:
                            await event.respond(error_message, parse_mode="html")
                            
                        await asyncio.sleep(5)
                        try:
                            await loading_msg.delete()
                        except Exception:
                            pass
                        return
                    
                    response = await conv.get_response()
                    await rc.delete()
                    
                    if response.media:
                        reply_to = event.reply_to_msg_id if event.is_reply else None
                        await client.send_file(
                            event.chat_id,
                            response.media,
                            caption="<blockquote>⚝ sꜰᴡ изобᴩᴀжᴇниᴇ</blockquote>",
                            reply_to=reply_to,
                            parse_mode="html"
                        )
                        await response.delete()
                        try:
                            await loading_msg.delete()
                        except Exception:
                            pass
                    else:
                        error_message = "<blockquote>⚝ оɯибᴋᴀ: нᴇ удᴀᴧоᴄь ᴨоᴧучиᴛь изобᴩᴀжᴇниᴇ</blockquote>"
                        
                        try:
                            await loading_msg.edit(error_message, parse_mode="html")
                        except Exception:
                            await event.respond(error_message, parse_mode="html")
                            
                        await asyncio.sleep(5)
                        try:
                            await loading_msg.delete()
                        except Exception:
                            pass
            
            except Exception as e:
                error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
                
                try:
                    await loading_msg.edit(error_message, parse_mode="html")
                except Exception:
                    await event.respond(error_message, parse_mode="html")
                    
                await asyncio.sleep(5)
                try:
                    await loading_msg.delete()
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Critical error in sfw_handler: {str(e)}")
    
    @client.on(events.NewMessage(pattern=r'\.furry'))
    async def furry_handler(event):
        try:
            if not await check_owner(event):
                return  
                
            can_edit = event.out
            
            try:
                if can_edit:
                    loading_msg = await event.edit("<blockquote>⚝ зᴀᴦᴩузᴋᴀ ɸуᴩᴩи изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
                else:
                    loading_msg = await event.respond("<blockquote>⚝ зᴀᴦᴩузᴋᴀ ɸуᴩᴩи изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
            except Exception as e:
                logger.warning(f"Failed to edit/send loading message: {str(e)}")
                loading_msg = await event.respond("<blockquote>⚝ зᴀᴦᴩузᴋᴀ ɸуᴩᴩи изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
                can_edit = False
                
            try:
                await asyncio.sleep(0.5)
                chat = "furrylov"
                
                result = await client(
                    functions.messages.GetHistoryRequest(
                        peer=chat,
                        offset_id=0,
                        offset_date=datetime.datetime.now(),
                        add_offset=random.choice(range(1, 12436, 2)),
                        limit=1,
                        max_id=0,
                        min_id=0,
                        hash=0,
                    ),
                )
                
                if result.messages and result.messages[0].media:
                    reply_to = event.reply_to_msg_id if event.is_reply else None
                    await client.send_file(
                        event.chat_id,
                        result.messages[0].media,
                        caption="<blockquote>⚝ ɸуᴩᴩи изобᴩᴀжᴇниᴇ</blockquote>",
                        reply_to=reply_to,
                        parse_mode="html"
                    )
                    try:
                        await loading_msg.delete()
                    except Exception:
                        pass
                else:
                    error_message = "<blockquote>⚝ оɯибᴋᴀ: нᴇ удᴀᴧоᴄь ᴨоᴧучиᴛь изобᴩᴀжᴇниᴇ</blockquote>"
                    
                    try:
                        await loading_msg.edit(error_message, parse_mode="html")
                    except Exception:
                        await event.respond(error_message, parse_mode="html")
                        
                    await asyncio.sleep(5)
                    try:
                        await loading_msg.delete()
                    except Exception:
                        pass
            
            except Exception as e:
                error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
                
                try:
                    await loading_msg.edit(error_message, parse_mode="html")
                except Exception:
                    await event.respond(error_message, parse_mode="html")
                    
                await asyncio.sleep(5)
                try:
                    await loading_msg.delete()
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Critical error in furry_handler: {str(e)}")
    
    @client.on(events.NewMessage(pattern=r'\.nsfw'))
    async def nsfw_handler(event):
        try:
            if not await check_owner(event):
                return  
                
            can_edit = event.out
            
            try:
                if can_edit:
                    loading_msg = await event.edit("<blockquote>⚝ зᴀᴦᴩузᴋᴀ ɴsꜰᴡ изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
                else:
                    loading_msg = await event.respond("<blockquote>⚝ зᴀᴦᴩузᴋᴀ ɴsꜰᴡ изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
            except Exception as e:
                logger.warning(f"Failed to edit/send loading message: {str(e)}")
                loading_msg = await event.respond("<blockquote>⚝ зᴀᴦᴩузᴋᴀ ɴsꜰᴡ изобᴩᴀжᴇния...</blockquote>", parse_mode="html")
                can_edit = False
                
            try:
                await asyncio.sleep(0.5)
                chat = "hdjrkdjrkdkd"
                
                result = await client(
                    functions.messages.GetHistoryRequest(
                        peer=chat,
                        offset_id=0,
                        offset_date=datetime.datetime.now(),
                        add_offset=random.choice(range(1, 851, 2)),
                        limit=1,
                        max_id=0,
                        min_id=0,
                        hash=0,
                    ),
                )
                
                if result.messages and result.messages[0].media:
                    reply_to = event.reply_to_msg_id if event.is_reply else None
                    await client.send_file(
                        event.chat_id,
                        result.messages[0].media,
                        caption="<blockquote>⚝ ɴsꜰᴡ изобᴩᴀжᴇниᴇ</blockquote>",
                        reply_to=reply_to,
                        parse_mode="html"
                    )
                    try:
                        await loading_msg.delete()
                    except Exception:
                        pass
                else:
                    error_message = "<blockquote>⚝ оɯибᴋᴀ: нᴇ удᴀᴧоᴄь ᴨоᴧучиᴛь изобᴩᴀжᴇниᴇ</blockquote>"
                    
                    try:
                        await loading_msg.edit(error_message, parse_mode="html")
                    except Exception:
                        await event.respond(error_message, parse_mode="html")
                        
                    await asyncio.sleep(5)
                    try:
                        await loading_msg.delete()
                    except Exception:
                        pass
            
            except Exception as e:
                error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
                
                try:
                    await loading_msg.edit(error_message, parse_mode="html")
                except Exception:
                    await event.respond(error_message, parse_mode="html")
                    
                await asyncio.sleep(5)
                try:
                    await loading_msg.delete()
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Critical error in nsfw_handler: {str(e)}")
    
    return [loli_handler, fem_handler, sfw_handler, furry_handler, nsfw_handler] 