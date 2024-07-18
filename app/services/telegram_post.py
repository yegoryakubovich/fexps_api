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
from aiogram.types import FSInputFile, InputMediaPhoto

from app.db.models import Session, TelegramPost, Actions
from app.repositories import TelegramPostRepository, CommissionPackRepository
from app.services.base import BaseService
from app.utils.bot.image import image_create, get_post_keyboard, get_post_text
from app.utils.decorators import session_required
from app.utils.exceptions import TelegramImagePathNotFound, TelegramMessageNotFound, TelegramPostNotFound
from config import settings


class TelegramPostService(BaseService):
    model = TelegramPost

    @session_required(permissions=['telegrams'], can_root=True)
    async def create_by_task(self, session: Session):
        bot = Bot(token=settings.telegram_token)
        for commission_pack in await CommissionPackRepository().get_list():
            if not commission_pack.telegram_chat_id or not commission_pack.filename:
                continue
            image_path = await image_create(commission_pack=commission_pack)
            if not image_path:
                raise TelegramImagePathNotFound(
                    kwargs={
                        'commission_pack_id': commission_pack.id,
                        'filename': commission_pack.filename,
                    },
                )
            message = await bot.send_photo(
                chat_id=commission_pack.telegram_chat_id,
                photo=FSInputFile(path=image_path),
                caption=get_post_text(),
                reply_markup=get_post_keyboard(),
            )
            if not message:
                raise TelegramMessageNotFound(
                    kwargs={
                        'commission_pack_id': commission_pack.id,
                    },
                )
            telegram_post = await TelegramPostRepository().create(
                commission_pack=commission_pack,
                message_id=message.message_id,
                text=message.caption,
            )
            await self.create_action(
                model=telegram_post,
                action=Actions.CREATE,
                parameters={
                    'creator': f'session_{session.id}',
                    'commission_pack': commission_pack.id,
                    'message_id': message.message_id,
                    'text': message.caption,
                },
            )
        return {}

    @session_required(permissions=['telegrams'], can_root=True)
    async def update_by_task(self, session: Session):
        bot = Bot(token=settings.telegram_token)
        for commission_pack in await CommissionPackRepository().get_list():
            if not commission_pack.telegram_chat_id or not commission_pack.filename:
                continue
            telegram_post = await TelegramPostRepository().get(commission_pack=commission_pack)
            if not telegram_post:
                raise TelegramPostNotFound(
                    kwargs={
                        'commission_pack_id': commission_pack.id,
                    },
                )
            image_path = await image_create(commission_pack=commission_pack)
            if not image_path:
                raise TelegramImagePathNotFound(
                    kwargs={
                        'commission_pack_id': commission_pack.id,
                        'filename': commission_pack.filename,
                    },
                )
            await bot.edit_message_media(
                chat_id=commission_pack.telegram_chat_id,
                message_id=telegram_post.message_id,
                media=InputMediaPhoto(media=FSInputFile(path=image_path), caption=telegram_post.text),
                reply_markup=get_post_keyboard(),
            )
            await self.create_action(
                model=telegram_post,
                action=Actions.UPDATE,
                parameters={
                    'updater': f'session_{session.id}',
                },
            )
        return {}
