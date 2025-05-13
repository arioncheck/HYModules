# meta developer: @ElonModules
# description: Модуль для получения информации о профиле игрока DDraceNetwork и KOG
# command: .ddnet - `Получить информацию о профиле игрока DDraceNetwork`
# command: .kog - `Получить информацию о профиле игрока KOG`

import requests
import urllib.parse
import asyncio
from bs4 import BeautifulSoup
import logging
from telethon import events
from userbot import client, is_owner

logger = logging.getLogger(__name__)

def register_handlers(client):
    @client.on(events.NewMessage(pattern=r'\.ddnet(?:\s+(.+))?'))
    async def ddnet_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            args = event.pattern_match.group(1)
            
            if not args:
                reply = await event.get_reply_message()
                if reply:
                    original_name = reply.message
                else:
                    error_message = "<blockquote>⚝ иʍя иᴦᴩоᴋᴀ нᴇ уᴋᴀзᴀно</blockquote>"
                    if can_edit:
                        await event.edit(error_message, parse_mode="html")
                    else:
                        await event.respond(error_message, parse_mode="html")
                    return
            else:
                original_name = args
            
            original_name = str(original_name)
            api_name = urllib.parse.quote_plus(original_name)
            
            fetching_message = f"<blockquote>⚝ ᴨоᴧучᴀю инфоᴩʍᴀцию о иᴦᴩоᴋᴇ DDraceNetwork <code>{original_name}</code>...</blockquote>"
            
            if can_edit:
                message = await event.edit(fetching_message, parse_mode="html")
            else:
                message = await event.respond(fetching_message, parse_mode="html")
            
            await asyncio.sleep(2)  
            
            try:
                response = requests.get(f"https://ddnet.org/players/?json2={api_name}", 
                                        headers={'Accept': 'application/json'})
                
                if response.status_code != 200:
                    error_message = "<blockquote>⚝ нᴇ удᴀᴧоᴄь ᴨоᴧучить инфоᴩʍᴀцию о ᴨᴩофиᴧᴇ</blockquote>"
                    if can_edit:
                        await message.edit(error_message, parse_mode="html")
                    else:
                        await message.respond(error_message, parse_mode="html")
                    return
                
                data = response.json()
                
                if not data or 'points' not in data:
                    error_message = "<blockquote>⚝ нᴇ удᴀᴧоᴄь ᴨоᴧучить инфоᴩʍᴀцию о ᴨᴩофиᴧᴇ</blockquote>"
                    if can_edit:
                        await message.edit(error_message, parse_mode="html")
                    else:
                        await message.respond(error_message, parse_mode="html")
                    return
                
                points = data['points']['points']
                rank = data['points']['rank']
                hours = data.get('hours_played_past_365_days', 0)
                
                hours_str = str(hours)
                
                def get_map_data(map_type):
                    if map_type in data.get('types', {}):
                        maps = data['types'][map_type]['maps']
                        completed = sum(1 for _ in maps.values() if _['finishes'] > 0)
                        total = len(maps)
                        return completed, total
                    return 0, 0  
                
                novice_completed, novice_total = get_map_data('Novice')
                moderate_completed, moderate_total = get_map_data('Moderate')
                brutal_completed, brutal_total = get_map_data('Brutal')
                insane_completed, insane_total = get_map_data('Insane')
                dummy_completed, dummy_total = get_map_data('Dummy')
                ddmax_easy_completed, ddmax_easy_total = get_map_data('DDmaX.Easy')
                ddmax_next_completed, ddmax_next_total = get_map_data('DDmaX.Next')
                ddmax_pro_completed, ddmax_pro_total = get_map_data('DDmaX.Pro')
                ddmax_nut_completed, ddmax_nut_total = get_map_data('DDmaX.Nut')
                oldschool_completed, oldschool_total = get_map_data('Oldschool')
                solo_completed, solo_total = get_map_data('Solo')
                race_completed, race_total = get_map_data('Race')
                fun_completed, fun_total = get_map_data('Fun')
                
                points_info = f"<blockquote>⚝ инфоᴩʍᴀция о иᴦᴩоᴋᴇ DDraceNetwork</blockquote>\n\n" \
                              f"<blockquote>⚝ ниᴋ: <code>{original_name}</code>\n" \
                              f"⚝ нᴀиᴦᴩᴀно: <code>{hours_str} чᴀᴄоʙ</code>\n" \
                              f"⚝ ᴨоинᴛы: <code>{points}</code>\n" \
                              f"⚝ ʍᴇᴄᴛо ʙ ᴛоᴨᴇ: <code>{rank}</code>\n" \
                              f"⚝ <a href='https://ddnet.org/players/{api_name}'>ᴄᴄыᴧᴋᴀ нᴀ ᴄᴛᴀᴛиᴄᴛиᴋу</a></blockquote>\n" \
                              f"<blockquote>⚝ ᴋоᴧичᴇᴄᴛʙо ᴨᴩойдᴇнных ᴋᴀᴩᴛ:\n" \
                              f" ⚝ Novice: <code>{novice_completed}/{novice_total}</code>\n" \
                              f" ⚝ Moderate: <code>{moderate_completed}/{moderate_total}</code>\n" \
                              f" ⚝ Brutal: <code>{brutal_completed}/{brutal_total}</code>\n" \
                              f" ⚝ Insane: <code>{insane_completed}/{insane_total}</code>\n" \
                              f" ⚝ Dummy: <code>{dummy_completed}/{dummy_total}</code>\n" \
                              f" ⚝ DDmaX.Easy: <code>{ddmax_easy_completed}/{ddmax_easy_total}</code>\n" \
                              f" ⚝ DDmaX.Next: <code>{ddmax_next_completed}/{ddmax_next_total}</code>\n" \
                              f" ⚝ DDmaX.Pro: <code>{ddmax_pro_completed}/{ddmax_pro_total}</code>\n" \
                              f" ⚝ DDmaX.Nut: <code>{ddmax_nut_completed}/{ddmax_nut_total}</code>\n" \
                              f" ⚝ Oldschool: <code>{oldschool_completed}/{oldschool_total}</code>\n" \
                              f" ⚝ Solo: <code>{solo_completed}/{solo_total}</code>\n" \
                              f" ⚝ Race: <code>{race_completed}/{race_total}</code>\n" \
                              f" ⚝ Fun: <code>{fun_completed}/{fun_total}</code></blockquote>"
                
                if can_edit:
                    await message.edit(points_info, parse_mode="html")
                else:
                    await message.respond(points_info, parse_mode="html")
                
            except Exception as e:
                error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
                if can_edit:
                    await message.edit(error_message, parse_mode="html")
                else:
                    await message.respond(error_message, parse_mode="html")
        except Exception as e:
            logger.error(f"Ошибка в ddnet_handler: {str(e)}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if event.out:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")

    @client.on(events.NewMessage(pattern=r'\.kog(?:\s+(.+))?'))
    async def kog_handler(event):
        try:
            if not await is_owner(event) and not event.out:
                return
                
            can_edit = event.out
            args = event.pattern_match.group(1)
            
            if not args:
                reply = await event.get_reply_message()
                if reply:
                    player_name = reply.message
                else:
                    error_message = "<blockquote>⚝ иʍя иᴦᴩоᴋᴀ нᴇ уᴋᴀзᴀно</blockquote>"
                    if can_edit:
                        await event.edit(error_message, parse_mode="html")
                    else:
                        await event.respond(error_message, parse_mode="html")
                    return
            else:
                player_name = args.strip()
            
            fetching_message = f"<blockquote>⚝ ᴨоᴧучᴀю инфоᴩʍᴀцию о иᴦᴩоᴋᴇ KOG <code>{player_name}</code>...</blockquote>"
            
            if can_edit:
                message = await event.edit(fetching_message, parse_mode="html")
            else:
                message = await event.respond(fetching_message, parse_mode="html")
            
            await asyncio.sleep(2)
            
            player_info = get_player_info(player_name)
            
            if player_info:
                played_hours = convert_time_to_hours(player_info.get('Hours', '0 months, 0 days, 0 hours, 0 minutes, 0 seconds'))
                
                output = f"<blockquote>⚝ инфоᴩʍᴀция о иᴦᴩоᴋᴇ KOG</blockquote>\n\n" \
                         f"<blockquote>⚝ ниᴋ: <code>{player_info.get('Nickname', 'нᴇᴛу')}</code>\n" \
                         f"⚝ нᴀиᴦᴩᴀно: <code>{played_hours} чᴀᴄоʙ</code>\n" \
                         f"⚝ ᴨоинᴛы: <code>{player_info.get('Points', 'нᴇᴛу')}</code>\n" \
                         f"⚝ ʍᴇᴄᴛо ʙ ᴛоᴨᴇ: <code>{player_info.get('Rank', 'нᴇᴛу')}</code>\n" \
                         f"⚝ <a href='{player_info.get('Stats Link', '')}'>ᴄᴄыᴧᴋᴀ нᴀ ᴄᴛᴀᴛиᴄᴛиᴋу</a></blockquote>"
                
                if can_edit:
                    await message.edit(output, parse_mode="html")
                else:
                    await message.respond(output, parse_mode="html")
                
            else:
                error_message = "<blockquote>⚝ нᴇ удᴀᴧоᴄь ᴨоᴧучить инфоᴩʍᴀцию о ᴨᴩофиᴧᴇ KOG</blockquote>"
                if can_edit:
                    await message.edit(error_message, parse_mode="html")
                else:
                    await message.respond(error_message, parse_mode="html")
                
        except Exception as e:
            logger.error(f"Ошибка в kog_handler: {str(e)}")
            error_message = f"<blockquote>⚝ оɯибᴋᴀ: {str(e)}</blockquote>"
            if event.out:
                await event.edit(error_message, parse_mode="html")
            else:
                await event.respond(error_message, parse_mode="html")
    
    return [ddnet_handler, kog_handler]

def convert_time_to_hours(time_str):
    months, days, hours, minutes, seconds = 0, 0, 0, 0, 0
    
    time_parts = time_str.split(', ')
    for part in time_parts:
        if 'months' in part:
            months = int(part.split()[0])
        elif 'days' in part:
            days = int(part.split()[0])
        elif 'hours' in part:
            hours = int(part.split()[0])
        elif 'minutes' in part:
            minutes = int(part.split()[0])
        elif 'seconds' in part:
            seconds = int(part.split()[0])

    total_hours = (months * 30 * 24) + (days * 24) + hours + (minutes / 60) + (seconds / 3600)
    return round(total_hours, 2)

def get_player_info(player_name):
    url = f"https://kog.tw/get.php?p=players&p=players&player={player_name}"

    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"Ошибка доступа к {url}: статус {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        info = {}

        nickname = soup.find('h2')
        info['Nickname'] = nickname.text.strip() if nickname else 'нᴇᴛу'

        wasted_time_header = soup.find('h5', text=lambda text: text and 'Wasted time due to finished maps' in text)
        if wasted_time_header:
            time_str = wasted_time_header.find_next('h6')
            info['Hours'] = time_str.text.strip() if time_str else 'нᴇᴛу'
        else:
            info['Hours'] = 'нᴇᴛу'

        rank_info = soup.find(text=lambda text: 'Rank' in text)
        if rank_info:
            rank_element = rank_info.find_next('b')
            info['Rank'] = rank_element.text.strip() if rank_element else 'нᴇᴛу'
            points_info = rank_info.find_next(text=lambda text: 'with' in text)
            info['Points'] = points_info.split()[1].strip() if points_info else 'нᴇᴛу'
        else:
            info['Rank'] = 'нᴇᴛу'
            info['Points'] = 'нᴇᴛу'

        info['Stats Link'] = f"https://kog.tw/index.php#p=players&player={player_name}"

        return info
    except Exception as e:
        logger.error(f"Ошибка при получении данных игрока KOG: {str(e)}")
        return None 