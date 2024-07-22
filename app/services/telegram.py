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

from app.db.models import Session, TelegramPost, Actions, CommissionPackTelegramTypes
from app.repositories import TelegramPostRepository, CommissionPackRepository
from app.services.base import BaseService
from app.utils.bot.images.sowapay import post_create_sowapay
from app.utils.decorators import session_required
from app.utils.exceptions import TelegramImagePathNotFound, TelegramMessageNotFound
from config import settings


class TelegramService(BaseService):
    model = TelegramPost

    @session_required(permissions=['telegrams'], can_root=True)
    async def create_by_task(self, session: Session):
        bot = Bot(token=settings.telegram_token)
        warnings = []
        for commission_pack in await CommissionPackRepository().get_list():
            if not commission_pack.telegram_chat_id or not commission_pack.telegram_type:
                continue
            posts_datas = None
            if commission_pack.telegram_type == CommissionPackTelegramTypes.FEXPS:
                posts_datas = None
            elif commission_pack.telegram_type == CommissionPackTelegramTypes.SOWAPAY:
                posts_datas = await post_create_sowapay(commission_pack=commission_pack)
            if not posts_datas:
                warnings += [
                    TelegramImagePathNotFound.message.format(
                        commission_pack_id=commission_pack.id,
                    ),
                ]
                continue
            messages_data = {}
            for post_data in posts_datas:
                name = post_data.get('name')
                image = post_data.get('image')
                text = post_data.get('text')
                reply_markup = post_data.get('reply_markup')
                if image:
                    message = await bot.send_photo(
                        chat_id=commission_pack.telegram_chat_id,
                        photo=FSInputFile(path=image),
                        caption=text,
                        reply_markup=reply_markup,
                    )
                else:
                    message = await bot.send_message(
                        chat_id=commission_pack.telegram_chat_id,
                        text=text,
                        reply_markup=reply_markup,
                    )
                if not message:
                    warnings += [
                        TelegramMessageNotFound.message.format(
                            commission_pack_id=commission_pack.id,
                        ),
                    ]
                    continue
                messages_data[name] = message.message_id
            if not messages_data:
                continue
            telegram_post = await TelegramPostRepository().create(commission_pack=commission_pack, data=messages_data)
            await self.create_action(
                model=telegram_post,
                action=Actions.CREATE,
                parameters={
                    'creator': f'session_{session.id}',
                    'commission_pack': commission_pack.id,
                    'data': messages_data,
                },
            )
        return {
            'warnings': warnings,
        }

    @session_required(permissions=['telegrams'], can_root=True)
    async def update_by_task(self, session: Session):
        bot = Bot(token=settings.telegram_token)
        warnings = []
        for commission_pack in await CommissionPackRepository().get_list():
            if not commission_pack.telegram_chat_id or not commission_pack.telegram_type:
                continue
            telegram_post = await TelegramPostRepository().get(commission_pack=commission_pack)
            if not telegram_post:
                warnings += [
                    TelegramMessageNotFound.message.format(
                        commission_pack_id=commission_pack.id,
                    ),
                ]
                continue
            message_data = telegram_post.data
            posts_datas = None
            if commission_pack.telegram_type == CommissionPackTelegramTypes.FEXPS:
                posts_datas = None
            elif commission_pack.telegram_type == CommissionPackTelegramTypes.SOWAPAY:
                posts_datas = await post_create_sowapay(commission_pack=commission_pack)
            if not posts_datas:
                warnings += [
                    TelegramImagePathNotFound.message.format(
                        commission_pack_id=commission_pack.id,
                    ),
                ]
                continue
            for post_data in posts_datas:
                name = post_data.get('name')
                message_id = message_data[name]
                image = post_data.get('image')
                text = post_data.get('text')
                reply_markup = post_data.get('reply_markup')
                if image:
                    await bot.edit_message_media(
                        chat_id=commission_pack.telegram_chat_id,
                        message_id=message_id,
                        media=InputMediaPhoto(
                            media=FSInputFile(path=image),
                            caption=text,
                        ),
                        reply_markup=reply_markup,
                    )
                else:
                    await bot.edit_message_text(
                        chat_id=commission_pack.telegram_chat_id,
                        message_id=message_id,
                        text=text,
                        reply_markup=reply_markup,
                    )
            await self.create_action(
                model=telegram_post,
                action=Actions.UPDATE,
                parameters={
                    'updater': f'session_{session.id}',
                },
            )
        return {
            'warnings': warnings,
        }
