from src.aram_champion_generator.aram_ramdom_2team import generate_image
from src.discord_function.send_image_base64 import send_base64_image
from src.analyze.cache_stats import get_cache_stats, get_cache_stats_more
import datetime
from src.aram_champion_generator.aram_ramdom_2team import (
    _last_blue_team_ids, _last_red_team_ids,
    _version_cache, _version_cache_time,
    _champions_cache, _champions_cache_time,
    _tag_champion_cache, _tag_champion_cache_time
)

async def handle_aram_random(message):
    try:
        base64_string = generate_image()
        await send_base64_image(message, base64_string, "Fighting!!")
    except Exception as err:
        print(f'Error generating image: {err}')
        await message.channel.send('Failed to generate image.')

async def handle_champion_help(message, path='docs/help_text.txt'):
    try:
        with open(path, encoding='utf-8') as f:
            help_text = f.read()
        await message.channel.send(help_text)
    except Exception as err:
        await message.channel.send(f'Failed to read {path}')

async def handle_champion_cache(message):
    stats = get_cache_stats()
    cache_time = stats['cache_time']
    if cache_time:
        cache_time_str = datetime.datetime.fromtimestamp(cache_time).strftime('%d/%m/%Y - %H:%M:%S')
    else:
        cache_time_str = 'N/A'
    msg = (
        f"Version: {stats['version']}\n"
        f"Số tướng cache: {stats['champion_count']}\n"
        f"Số tag cache: {stats['tag_count']}\n"
        f"Thời gian cache: {cache_time_str}"
    )
    await message.channel.send(msg)

async def handle_champion_cache_more(message):
    stats = get_cache_stats_more()
    cache_time = stats['cache_time']
    if cache_time:
        cache_time_str = datetime.datetime.fromtimestamp(cache_time).strftime('%d/%m/%Y - %H:%M:%S')
    else:
        cache_time_str = 'N/A'
    cache_age = stats['cache_age_hours']
    if cache_age is not None:
        cache_age_str = f"{cache_age:.2f} giờ"
    else:
        cache_age_str = 'N/A'
    cache_expire_hr = int(stats['cache_expire']/3600)
    msg = (
        f"Version: {stats['version']}\n"
        f"Link API: {stats['api_url']}\n"
        f"Số tag cache: {stats['tag_count']}\n"
        f"Danh sách tag: {', '.join(stats['tag_list'])}\n"
        f"Thời gian cache: {cache_time_str}\n"
        f"Cache đã lưu: {cache_age_str}\n"
        f"Cache tối đa: {cache_expire_hr} giờ"
    )
    await message.channel.send(msg)

async def handle_clear_team_cache(message):
    _last_blue_team_ids.clear()
    _last_red_team_ids.clear()
    await message.channel.send('Đã xóa cache team (2 đội random gần nhất)!')

async def handle_clear_all_cache(message):
    global _version_cache, _version_cache_time
    _version_cache = None
    _version_cache_time = 0
    _champions_cache.clear()
    _champions_cache_time.clear()
    _tag_champion_cache.clear()
    _tag_champion_cache_time.clear()
    _last_blue_team_ids.clear()
    _last_red_team_ids.clear()
    await message.channel.send('Đã xóa toàn bộ cache bot!') 