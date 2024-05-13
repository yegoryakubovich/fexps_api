#
# (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from aiogram import Bot
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InputMediaPhoto, InlineKeyboardButton, Message

from config import settings


def get_post_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='СДЕЛАТЬ ОБМЕН', url=settings.telegram_manager)],
            [InlineKeyboardButton(text='О НАС', url=settings.telegram_about)],
            [InlineKeyboardButton(text='КАК ПРОХОДИТ ОБМЕН', url=settings.telegram_info)],
            [InlineKeyboardButton(text='ОТЗЫВЫ', url=settings.telegram_reviews)],
        ],
    )
    return keyboard


async def send_message(
        text: str = None,
        photo: [str, FSInputFile] = None,
        keyboard: InlineKeyboardMarkup = None,
) -> Message:
    bot = Bot(token=settings.telegram_token)
    message = None
    async with bot:
        if photo:
            message = await bot.send_photo(
                chat_id=settings.telegram_chat_id,
                caption=text,
                photo=photo,
                reply_markup=keyboard,
            )
        elif text:
            message = await bot.send_message(chat_id=settings.telegram_chat_id, text=text, reply_markup=keyboard)
    return message


async def edit_message(
        message_id: int,
        text: str = None,
        photo: [str, FSInputFile] = None,
        keyboard: InlineKeyboardMarkup = None,
) -> None:
    bot = Bot(token=settings.telegram_token)
    async with bot:
        if photo:
            await bot.edit_message_media(
                chat_id=settings.telegram_chat_id,
                message_id=message_id,
                media=InputMediaPhoto(media=photo, caption=text),
                reply_markup=keyboard,
            )
        elif text:
            await bot.edit_message_text(
                chat_id=settings.telegram_chat_id,
                message_id=message_id,
                text=text,
                reply_markup=keyboard,
            )
