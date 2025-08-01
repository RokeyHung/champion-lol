import sys
import os
import random

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

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
        with open(resource_path(path), encoding='utf-8') as f:
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
        f"Number of cached champions: {stats['champion_count']}\n"
        f"Number of cached tags: {stats['tag_count']}\n"
        f"Cache time: {cache_time_str}"
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
        cache_age_str = f"{cache_age:.2f} hours"
    else:
        cache_age_str = 'N/A'
    cache_expire_hr = int(stats['cache_expire']/3600)
    msg = (
        f"Version: {stats['version']}\n"
        f"Link API: {stats['api_url']}\n"
        f"Number of cached tags: {stats['tag_count']}\n"
        f"Tag list: {', '.join(stats['tag_list'])}\n"
        f"Cache time: {cache_time_str}\n"
        f"Cache age: {cache_age_str}\n"
        f"Cache max: {cache_expire_hr} hours"
    )
    await message.channel.send(msg)

async def handle_clear_team_cache(message):
    _last_blue_team_ids.clear()
    _last_red_team_ids.clear()
    await message.channel.send('Team cache (2 most recent random teams) cleared!')

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
    await message.channel.send('All bot cache cleared!')

async def handle_call_teams(message):
    if not message.guild:
        await message.channel.send('This command can only be used in a server.')
        return
    voice_channels = [ch for ch in message.guild.channels if ch.type.name == 'voice']
    voice_channels.sort(key=lambda c: c.position)
    found = False
    for i in range(len(voice_channels) - 1):
        ch1, ch2 = voice_channels[i], voice_channels[i+1]
        if len(ch1.members) == 0 and len(ch2.members) == 0:
            # Ensure not first and last (no wrap-around)
            if i == 0 and i+1 == len(voice_channels)-1:
                continue
            found = True
            await message.channel.send(
                f"Please join the call rooms for the match!\nBlue Team: <#{ch1.id}>\nRed Team: <#{ch2.id}>"
            )
            break
    if not found:
        await message.channel.send('Could not find two adjacent empty voice channels!')
    return 