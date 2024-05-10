from aiogram import Bot
from aiogram.types import FSInputFile

from app.tasks.permanents.telegram.image_poster.image import image_create
from config import settings


async def send_message(text: str = None, photo: [str, FSInputFile] = None):
    bot = Bot(token=settings.bot_token)
    if photo:
        async with bot:
            await bot.send_photo(chat_id=settings.channel_id, caption=text, photo=photo)
    elif text:
        async with bot:
            await bot.send_message(chat_id=settings.channel_id, text=text)

