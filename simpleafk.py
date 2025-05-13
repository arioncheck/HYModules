# meta developer: @qveroz
# description: Простой AFK модуль для уведомления о вашем отсутствии
# command: .safk [причина] - `Включить AFK режим с опциональной причиной`
# command: .sunafk - `Выключить AFK режим`

import time
from datetime import datetime
from telethon import events
from telethon.tl.types import User
from userbot import client

afk_enabled = False
afk_reason = None
afk_time = None

def format_time_passed(start_time):
    now = datetime.now().replace(microsecond=0)
    start = datetime.fromtimestamp(start_time).replace(microsecond=0)
    diff = now - start
    
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}д {hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def register_handlers(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r'\.safk(?:\s+(.*))?'))
    async def safk_handler(event):
        global afk_enabled, afk_reason, afk_time
        
        afk_reason = event.pattern_match.group(1)
        afk_time = time.time()
        afk_enabled = True
        
        if afk_reason:
            msg = "<blockquote>⚝ AFK ᴩᴇжиʍ ʙᴋᴧючᴇн</blockquote>\n<blockquote>⚝ Пᴩичинᴀ: {}</blockquote>".format(afk_reason)
        else:
            msg = "<blockquote>⚝ AFK ᴩᴇжиʍ ʙᴋᴧючᴇн</blockquote>"
            
        try:
            await event.edit(msg, parse_mode="html")
        except Exception:
            pass
    
    @client.on(events.NewMessage(outgoing=True, pattern=r'\.sunafk'))
    async def sunafk_handler(event):
        global afk_enabled, afk_reason, afk_time
        
        if not afk_enabled:
            try:
                await event.edit("<blockquote>⚝ AFK ᴩᴇжиʍ нᴇ ʙᴋᴧючᴇн</blockquote>", parse_mode="html")
            except Exception:
                pass
            return
        
        time_passed = format_time_passed(afk_time)
        afk_enabled = False
        afk_reason = None
        afk_time = None
        
        try:
            await event.edit("<blockquote>⚝ AFK ᴩᴇжиʍ ʙыᴋᴧючᴇн</blockquote>\n<blockquote>⚝ Пᴩоʙᴇᴧ ʙ AFK: {}</blockquote>".format(time_passed), parse_mode="html")
        except Exception:
            pass
    
    @client.on(events.NewMessage(outgoing=True))
    async def reset_afk(event):
        global afk_enabled, afk_reason, afk_time
        
        if not afk_enabled:
            return
            
        if event.raw_text.startswith(('.safk', '.sunafk')):
            return
            
        time_passed = format_time_passed(afk_time)
        afk_enabled = False
        afk_reason = None
        afk_time = None
    
    @client.on(events.NewMessage(incoming=True))
    async def afk_reply(event):
        global afk_enabled, afk_reason, afk_time
        
        if not afk_enabled:
            return
        
        try:
            if not hasattr(event, 'message'):
                return
                
            message = event.message
            if not message:
                return
            
            if not hasattr(event, 'is_private'):
                return
                
            is_private = event.is_private
            
            if not hasattr(message, 'mentioned'):
                return
                
            is_mentioned = message.mentioned
            
            if not (is_private or is_mentioned):
                return
                
            try:
                sender = await event.get_sender()
                if not sender or not isinstance(sender, User):
                    return
                    
                if sender.bot:
                    return
            except Exception:
                return
            
            time_passed = format_time_passed(afk_time)
            
            if afk_reason:
                reply = "<blockquote>⚝ Я ᴄᴇйчᴀᴄ AFK</blockquote>\n<blockquote>⚝ Ушᴇᴧ: {} нᴀзᴀд</blockquote>\n<blockquote>⚝ Пᴩичинᴀ: {}</blockquote>".format(time_passed, afk_reason)
            else:
                reply = "<blockquote>⚝ Я ᴄᴇйчᴀᴄ AFK</blockquote>\n<blockquote>⚝ Ушᴇᴧ: {} нᴀзᴀд</blockquote>".format(time_passed)
                
            await event.reply(reply, parse_mode="html")
            
        except Exception:
            pass
            
    return [safk_handler, sunafk_handler, reset_afk, afk_reply] 