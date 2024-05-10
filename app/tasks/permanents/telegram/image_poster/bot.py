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
from aiogram.types import FSInputFile

from config import settings


async def send_message(text: str = None, photo: [str, FSInputFile] = None):
    bot = Bot(token=settings.bot_token)
    if photo:
        async with bot:
            await bot.send_photo(chat_id=settings.channel_id, caption=text, photo=photo)
    elif text:
        async with bot:
            await bot.send_message(chat_id=settings.channel_id, text=text)
