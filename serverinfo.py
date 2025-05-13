# meta developer: @hikarimods
# description: Показывает информацию о сервере
# command: .serverinfo - `Показать информацию о сервере`

import contextlib
import os
import platform
import sys
import logging

import psutil
from telethon import events
from userbot import client, is_owner

logger = logging.getLogger(__name__)

def bytes_to_megabytes(b: int) -> int:
    return round(b / 1024 / 1024, 1)

def register_handlers(client):
    strings = {
        "loading": "<blockquote>⚝ зᴀᴦᴩузᴋᴀ инфоᴩʍᴀции о ᴄᴇᴩʙᴇᴩᴇ...</blockquote>",
        "servinfo": (
            "<blockquote>⚝ инфоᴩʍᴀция о ᴄᴇᴩʙᴇᴩᴇ:\n\n"
            "⚝ CPU: {cpu} ядᴇᴩ(-ᴩо) {cpu_load}%\n"
            "⚝ RAM: {ram} / {ram_load_mb}MB ({ram_load}%)\n\n"
            "⚝ Kernel: {kernel}\n"
            "⚝ Arch: {arch}\n"
            "⚝ OS: {os}\n\n"
            "⚝ Python: {python}</blockquote>"
        ),
    }
    
    @client.on(events.NewMessage(pattern=r'\.serverinfo'))
    async def serverinfo_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            
            if can_edit:
                await event.edit(strings["loading"], parse_mode="html")
            else:
                await event.respond(strings["loading"], parse_mode="html")
            
            inf = {
                "cpu": "n/a",
                "cpu_load": "n/a",
                "ram": "n/a",
                "ram_load_mb": "n/a",
                "ram_load": "n/a",
                "kernel": "n/a",
                "arch": "n/a",
                "os": "n/a",
                "python": "n/a",
            }

            with contextlib.suppress(Exception):
                inf["cpu"] = psutil.cpu_count(logical=True)

            with contextlib.suppress(Exception):
                inf["cpu_load"] = psutil.cpu_percent()

            with contextlib.suppress(Exception):
                inf["ram"] = bytes_to_megabytes(
                    psutil.virtual_memory().total - psutil.virtual_memory().available
                )

            with contextlib.suppress(Exception):
                inf["ram_load_mb"] = bytes_to_megabytes(psutil.virtual_memory().total)

            with contextlib.suppress(Exception):
                inf["ram_load"] = psutil.virtual_memory().percent

            with contextlib.suppress(Exception):
                inf["kernel"] = platform.release()

            with contextlib.suppress(Exception):
                inf["arch"] = platform.architecture()[0]

            with contextlib.suppress(Exception):
                if platform.system() == "Linux":
                    try:
                        system = os.popen("cat /etc/*release").read()
                        b = system.find('DISTRIB_DESCRIPTION="') + 21
                        system = system[b : system.find('"', b)]
                        inf["os"] = system
                    except:
                        inf["os"] = platform.system() + " " + platform.release()
                elif platform.system() == "Windows":
                    inf["os"] = f"Windows {platform.release()} {platform.version()}"
                else:
                    inf["os"] = platform.system() + " " + platform.release()

            with contextlib.suppress(Exception):
                inf["python"] = (
                    f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                )

            result = strings["servinfo"].format(**inf)
            if can_edit:
                await event.edit(result, parse_mode="html")
            else:
                await event.respond(result, parse_mode="html")
                
        except Exception as e:
            logger.error(f"Error in serverinfo_handler: {e}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if can_edit:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")
    
    return [serverinfo_handler] 