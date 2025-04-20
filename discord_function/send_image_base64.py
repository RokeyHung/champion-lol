import base64
import io
from discord import File


async def send_base64_image(message, data_url, content=""):
  # Step 1: Extract base64 part from data URL
  base64_str = data_url.split(',')[1]

  # Step 2: Convert base64 string to bytes
  image_bytes = base64.b64decode(base64_str)

  # Step 3: Create the image attachment
  file = File(io.BytesIO(image_bytes), filename="image.png")

  # Step 4: Send the image in the message
  await message.channel.send(content=content, files=[file])
