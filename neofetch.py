# meta developer: @qveroz
# description: Показывает информацию о системе
# command: .neofetch - `Показать информацию о системе`

import os
import platform
import psutil
import time
import asyncio
from datetime import datetime, timedelta
from telethon import events, version
from userbot import client

def get_size(bytes, suffix="B"):
    """Преобразует байты в читаемый формат"""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor

def get_uptime():
    """Получает время работы системы"""
    try:
        if platform.system() == "Windows":
            boot_time = psutil.boot_time()
            boot_time_datetime = datetime.fromtimestamp(boot_time)
            current_time = datetime.now()
            uptime = current_time - boot_time_datetime
            return str(uptime).split('.')[0]
        else:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return str(timedelta(seconds=uptime_seconds)).split('.')[0]
    except:
        return "Неизвестно"

def get_system_info():
    """Собирает информацию о системе"""
    try:
        info = {}
        
        info["system"] = platform.system()
        info["release"] = platform.release()
        info["version"] = platform.version()
        
        svmem = psutil.virtual_memory()
        info["ram_total"] = get_size(svmem.total)
        info["ram_used"] = get_size(svmem.used)
        info["ram_percent"] = f"{svmem.percent}%"

        info["uptime"] = get_uptime()

        info["python_version"] = platform.python_version()
        info["telethon_version"] = version.__version__
        
        return info
    except Exception as e:
        return {"error": str(e)}

def format_neofetch(info):
    """Форматирует информацию о системе"""
    if "error" in info:
        return f"<blockquote>⚝ Ошибᴋᴀ: {info['error']}</blockquote>"
    
    text = f"""<blockquote>⚝ ОС: {info['system']} {info['release']}<br>
⚝ Оᴨᴇᴩᴀᴛиʙнᴀя ᴨᴀʍяᴛь: {info['ram_total']}<br>
⚝ Вᴩᴇʍя ᴩᴀбоᴛы: {info['uptime']}<br>
⚝ Python: {info['python_version']}<br>
⚝ Telethon: {info['telethon_version']}</blockquote>"""
    
    return text

def register_handlers(client):
    """
    Регистрирует обработчики модуля
    """
    @client.on(events.NewMessage(pattern=r'\.neofetch'))
    async def neofetch_handler(event):
        """Показать информацию о системе"""
        await event.edit("<blockquote>⚝ Собиᴩᴀю инфоᴩʍᴀцию...</blockquote>", parse_mode="html")
        
        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, get_system_info)

            formatted_info = format_neofetch(info)
            await event.edit(formatted_info, parse_mode="html")
        except Exception as e:
            await event.edit(f"<blockquote>⚝ Ошибᴋᴀ: {str(e)}</blockquote>", parse_mode="html")
    
    return neofetch_handler 