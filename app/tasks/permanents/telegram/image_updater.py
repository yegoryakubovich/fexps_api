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


import asyncio

from aiogram.types import FSInputFile

from app.repositories import TelegramPostRepository
from app.tasks.permanents.telegram.logger import TelegramLogger
from app.tasks.permanents.telegram.utils.bot import get_post_keyboard, edit_message
from app.tasks.permanents.telegram.utils.image import image_create

custom_logger = TelegramLogger(prefix='telegram_image_updater')


async def run():
    telegram_post = await TelegramPostRepository().get()
    if not telegram_post:
        custom_logger.critical(text='Not found telegram_post')
        return
    image_path = await image_create()
    await edit_message(
        message_id=telegram_post.message_id,
        photo=FSInputFile(path=image_path),
        text=telegram_post.text,
        keyboard=get_post_keyboard(),
    )
    await asyncio.sleep(60)


async def telegram_image_updater():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
