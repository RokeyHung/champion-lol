from dotenv import load_dotenv
import os
import asyncio

load_dotenv() 
from discord import Intents
from discord.ext import commands
from src.analyze.command_handler import (
    handle_aram_random,
    handle_champion_help,
    handle_champion_cache,
    handle_champion_cache_more,
    handle_clear_all_cache,
    handle_call_teams
)

# Initialize the bot with required intents
intents = Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

# Queue to serialize ARAM random requests
request_queue = asyncio.Queue()
_worker_task = None

async def _queue_worker():
    while True:
        message = await request_queue.get()
        try:
            await handle_aram_random(message)
        except Exception as err:
            try:
                await message.channel.send('An error occurred while processing !aram-random.')
            except Exception:
                pass
        finally:
            request_queue.task_done()


# Event: Bot is ready
@client.event
async def on_ready():
    print(f"✅ Bot is running as {client.user}")
    global _worker_task
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(_queue_worker())


# Event: Message is received
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:
        await handle_champion_help(message)
        return
    if message.content == '!champion-help':
        await handle_champion_help(message)
        return
    if message.content == '!champion-cache':
        await handle_champion_cache(message)
        return
    if message.content == '!champion-cache-more':
        await handle_champion_cache_more(message)
        return
    if message.content == '!aram-random':
        await request_queue.put(message)
        return
    if message.content == '!aram-random-summary':
        await handle_champion_help(message, "docs/team_champion_random_summary.txt")
        return
    if message.content == '!clear-all-cache':
        await handle_clear_all_cache(message)
        return
    if message.content == '!call-teams':
        await handle_call_teams(message)
        return
    if message.content == '!aram-rule':
        await handle_champion_help(message, "docs/aram-rule.txt")
        return


# Run the bot with your token
client.run(os.environ['DISCORD_TOKEN'])
