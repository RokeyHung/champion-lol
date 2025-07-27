from dotenv import load_dotenv
import os
import datetime

load_dotenv() 
from discord import Intents
from discord.ext import commands
from src.aram_champion_generator.aram_ramdom_2team import generate_image
from src.discord_function.send_image_base64 import send_base64_image
from src.analyze.cache_stats import get_cache_stats

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

    # Lệnh trợ giúp
    if message.content == '!champion-help':
        try:
            with open('help_text.txt', encoding='utf-8') as f:
                help_text = f.read()
            await message.channel.send(help_text)
        except Exception as err:
            print(f'Error reading help_text.txt: {err}')
            await message.channel.send('Failed to read help_text.txt')   
        return

    # Respond to the specific command
    if message.content == '!aram-random':
        try:
            base64_string = generate_image()
            await send_base64_image(message, base64_string, "Fighting!!")
        except Exception as err:
            print(f'Error generating image: {err}')
            await message.channel.send('Failed to generate image.')

    if message.content == '!champion-cache':
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
        return


# Run the bot with your token
client.run(os.environ['DISCORD_TOKEN'])
