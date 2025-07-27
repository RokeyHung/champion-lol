from dotenv import load_dotenv
import os

load_dotenv() 
from discord import Intents
from discord.ext import commands
from aram_champion_generator.aram_ramdom_2team import generate_image
from discord_function.send_image_base64 import send_base64_image

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

    # Respond to the specific command
    if message.content == '!aram-random':
        try:
            base64_string = await generate_image()
            await send_base64_image(message, base64_string, "Fighting!!")
        except Exception as err:
            print(f'Error generating image: {err}')
            await message.channel.send('❌ Failed to generate image.')


# Run the bot with your token
client.run(os.environ['DISCORD_TOKEN'])
