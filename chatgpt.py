# meta developer: @qveroz
# description: Модуль для работы с нейросетью
# command: .gpt <вопрос> - `Разговор с ИИ`
# command: .gptclear - `Очистить историю разговора`

import aiohttp
import json
from telethon import events
from userbot import client, is_owner
import logging
from telethon.errors.rpcerrorlist import MessageIdInvalidError

logger = logging.getLogger(__name__)

conversation_history = []
MAX_HISTORY = 20

def format_answer(text):
    if "```" not in text:
        return text.replace("\n", "<br>")
        
    parts = text.split("```")
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            lang = part.split("\n")[0] if "\n" in part else ""
            code = "\n".join(part.split("\n")[1:]) if "\n" in part else part
            result.append(f"<pre><code class='language-{lang}'>{code}</code></pre>")
        else:
            result.append(part.replace("\n", "<br>"))
    return "".join(result)

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

def register_handlers(client):
    """
    Регистрирует обработчики модуля
    """
    
    @client.on(events.NewMessage(pattern=r'\.gpt'))
    async def gpt_handler(event):
        """<вопрос> - Разговор с ИИ"""
        if not await is_owner(event):
            return
            
        global conversation_history
        
        args = event.text.split(' ', 1)
        question = args[1] if len(args) > 1 else ""
        
        if not question:
            await safe_edit(event, "<blockquote>⚝ нᴇᴛ ʙоᴨᴩоᴄᴀ.</blockquote>", parse_mode="html")
            return
        
        await safe_edit(event, "<blockquote>⚝ ᴦᴇнᴇᴩиᴩую оᴛʙᴇᴛ...</blockquote>", parse_mode="html")
        
        conversation_history.append({"role": "user", "content": question})
        
        if len(conversation_history) > MAX_HISTORY * 2:  
            conversation_history = conversation_history[-MAX_HISTORY * 2:]
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    "https://cablyai.com/v1/chat/completions",
                    headers={
                        'Authorization': 'Bearer sk-l4HU4KwZt6bF8gOwwKCOMpfpIKvR9YhDHvTFIGJ6tJ5rPKXE',
                        'Content-Type': 'application/json',
                    },
                    json={
                        "model": "gpt-4o",
                        "messages": conversation_history
                    }
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        answer = response_data["choices"][0]["message"]["content"]
                        
                        conversation_history.append({"role": "assistant", "content": answer})
                        
                        formatted_answer = format_answer(answer)
                        
                        response_text = f"<blockquote>⚝ ʙоᴨᴩоᴄ: <code>{question}</code></blockquote>\n\n"
                        response_text += f"<blockquote>⚝ оᴛʙᴇᴛ:\n{formatted_answer}</blockquote>"
                        
                        await safe_edit(event, response_text, parse_mode="html")
                    else:
                        await safe_edit(event, "<blockquote>⚝ оɯибᴋᴀ ᴨᴩи зᴀᴨᴩоᴄᴇ ᴋ ИИ.</blockquote>", parse_mode="html")
            except Exception as e:
                await safe_edit(event, f"<blockquote>⚝ оɯибᴋᴀ: <code>{str(e)}</code></blockquote>", parse_mode="html")
    
    @client.on(events.NewMessage(pattern=r'\.gptclear'))
    async def gptclear_handler(event):
        """Очистить историю разговора"""
        if not await is_owner(event):
            return
            
        global conversation_history
        
        conversation_history = []
        await safe_edit(event, "<blockquote>⚝ иᴄᴛоᴩия ᴩᴀзᴦоʙоᴩᴀ очищᴇнᴀ.</blockquote>", parse_mode="html")
    
    return gpt_handler 