from dotenv import load_dotenv
import os
import datetime

load_dotenv() 
from discord import Intents
from discord.ext import commands
from src.analyze.command_handler import (
    handle_aram_random,
    handle_champion_help,
    handle_champion_cache,
    handle_champion_cache_more
)

# Initialize the bot with required intents
intents = Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)


# Event: Bot is ready
@client.event
async def on_ready():
    print(f"✅ Bot đang chạy với tên {client.user}")


# Event: Message is received
@client.event
async def on_message(message):
    if message.author == client.user:
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
        await handle_aram_random(message)
        return


# Run the bot with your token
client.run(os.environ['DISCORD_TOKEN'])
