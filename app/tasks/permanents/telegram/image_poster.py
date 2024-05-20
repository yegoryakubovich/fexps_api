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


from aiogram.types import FSInputFile, Message

from app.repositories import TelegramPostRepository
from app.tasks.permanents.telegram.logger import TelegramLogger
from app.tasks.permanents.telegram.utils.bot import send_message, get_post_text, get_post_keyboard
from app.tasks.permanents.telegram.utils.image import image_create

custom_logger = TelegramLogger(prefix='telegram_image_poster')


async def telegram_image_poster():
    custom_logger.critical(text='Start post')
    image_path = await image_create()
    message: Message = await send_message(
        photo=FSInputFile(path=image_path),
        text=get_post_text(),
        keyboard=get_post_keyboard(),
    )
    if not message:
        custom_logger.critical(text='Not found message')
        return
    await TelegramPostRepository().create(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=message.caption,
    )
