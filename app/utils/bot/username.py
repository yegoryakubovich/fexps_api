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

from config import settings


async def get_bot_username() -> str:
    bot = Bot(token=settings.telegram_token)
    async with bot:
        bot_info = await bot.get_me()
    return bot_info.username


async def get_chat_username(chat_id: int) -> str:
    bot = Bot(token=settings.telegram_token)
    async with bot:
        bot_info = await bot.get_chat(chat_id)
    return bot_info.username
