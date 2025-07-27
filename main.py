from dotenv import load_dotenv
import os

load_dotenv() 
from discord import Intents
from discord.ext import commands
from src.analyze.command_handler import (
    handle_aram_random,
    handle_champion_help,
    handle_champion_cache,
    handle_champion_cache_more,
    handle_clear_team_cache,
    handle_clear_all_cache,
    handle_call_teams
)

# Initialize the bot with required intents
intents = Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)


# Event: Bot is ready
@client.event
async def on_ready():
    print(f"✅ Bot is running as {client.user}")


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
        await handle_aram_random(message)
        return
    if message.content == '!aram-random-summary':
        await handle_champion_help(message, "docs/team_champion_random_summary.txt")
        return
    if message.content == '!clear-team-cache':
        await handle_clear_team_cache(message)
        return
    if message.content == '!clear-all-cache':
        await handle_clear_all_cache(message)
        return
    if message.content == '!call-teams':
        await handle_call_teams(message)
        return


# Run the bot with your token
client.run(os.environ['DISCORD_TOKEN'])
