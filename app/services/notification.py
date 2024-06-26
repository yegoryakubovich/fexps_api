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


import logging
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, InputMediaPhoto

from app.db.models import NotificationSetting, Session, Actions, NotificationStates
from app.repositories import NotificationSettingRepository, NotificationHistoryRepository, TextRepository, \
    TelegramPostRepository
from app.services.base import BaseService
from app.utils.bot.image import image_create, get_post_keyboard, get_post_text
from app.utils.bot.username import get_bot_username, get_chat_username
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required
from app.utils.exceptions import NotificationTelegramAlreadyLinked
from config import settings


class NotificationService(BaseService):
    model = NotificationSetting

    @session_required()
    async def get(
            self,
            session: Session,
    ) -> dict:
        account = session.account
        notification_setting = await NotificationSettingRepository().get_by_account(account=account)
        if not notification_setting:
            notification_setting = await NotificationSettingRepository().create(account=account)
        return {
            'notification': await self.generate_notification_dict(notification_setting=notification_setting),
        }

    @session_required()
    async def update_code(
            self,
            session: Session,
    ) -> dict:
        account = session.account
        notification_setting = await NotificationSettingRepository().get_by_account(account=account)
        if notification_setting.telegram_id:
            raise NotificationTelegramAlreadyLinked()
        code = await create_id_str()
        await NotificationSettingRepository().update(
            notification_setting,
            code=code,
        )
        await self.create_action(
            model=notification_setting,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'code': code,
            },
        )
        bot_username = await get_bot_username()
        return {
            'code': code,
            'url': f'https://t.me/{bot_username}?start={code}'
        }

    @session_required()
    async def update_settings(
            self,
            session: Session,
            is_request: bool,
            is_requisite: bool,
            is_order: bool,
            is_chat: bool,
            is_transfer: bool,
            is_global: bool,
            is_active: bool,
    ) -> dict:
        account = session.account
        notification_setting = await NotificationSettingRepository().get_by_account(account=account)
        await NotificationSettingRepository().update(
            notification_setting,
            is_request=is_request,
            is_requisite=is_requisite,
            is_order=is_order,
            is_chat=is_chat,
            is_transfer=is_transfer,
            is_global=is_global,
            is_active=is_active,
        )
        await self.create_action(
            model=notification_setting,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'is_request': is_request,
                'is_requisite': is_requisite,
                'is_order': is_order,
                'is_chat': is_chat,
                'is_transfer': is_transfer,
                'is_global': is_global,
                'is_active': is_active,
            },
        )
        return {}

    @session_required(permissions=['notifications'], can_root=True)
    async def send_notification_by_task(self, session: Session):
        bot = Bot(token=settings.telegram_token)
        for notification in await NotificationHistoryRepository().get_list(state=NotificationStates.WAIT):
            notification_setting = notification.notification_setting
            account = notification_setting.account
            state = NotificationStates.SUCCESS
            error = None
            try:
                await bot.send_message(
                    chat_id=notification_setting.telegram_id,
                    text=notification.text,
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text=await TextRepository().get_by_key_or_none(
                                        key='notification_site_button',
                                        language=account.language,
                                    ),
                                    url=settings.site_url,
                                ),
                            ],
                        ],
                    ),
                )
            except TelegramForbiddenError:
                state = NotificationStates.BLOCKED
            except Exception as e:
                error = e
                state = NotificationStates.ERROR
            await NotificationHistoryRepository().update(notification, state=state)
            await self.create_action(
                model=notification_setting,
                action=Actions.UPDATE,
                parameters={
                    'notification_history': notification.id,
                    'state': state,
                    'error': error,
                },
            )
        return {}

    @session_required(permissions=['notifications'], can_root=True)
    async def send_image_by_task(self, session: Session):
        bot = Bot(token=settings.telegram_token)
        image_path = await image_create()
        if not image_path:
            logging.critical('Not found image')
            return {}
        message = await bot.send_photo(
            chat_id=settings.telegram_chat_id,
            photo=FSInputFile(path=image_path),
            caption=get_post_text(),
            reply_markup=get_post_keyboard(),
        )
        if not message:
            logging.critical('Not found message')
            return
        await TelegramPostRepository().create(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=message.caption,
        )
        return {}

    @session_required(permissions=['notifications'], can_root=True)
    async def update_image_by_task(self, session: Session):
        bot = Bot(token=settings.telegram_token)
        telegram_post = await TelegramPostRepository().get()
        if not telegram_post:
            logging.critical('Not found telegram_post')
            return
        image_path = await image_create()
        if not image_path:
            logging.critical('Not found image_path')
            return
        await bot.edit_message_media(
            chat_id=settings.telegram_chat_id,
            message_id=telegram_post.message_id,
            media=InputMediaPhoto(media=FSInputFile(path=image_path), caption=telegram_post.text),
            reply_markup=get_post_keyboard(),
        )
        return {}

    @staticmethod
    async def generate_notification_dict(notification_setting: NotificationSetting) -> Optional[dict]:
        if not notification_setting:
            return
        return {
            'id': notification_setting.id,
            'telegram_id': notification_setting.telegram_id,
            'username': await get_chat_username(chat_id=notification_setting.telegram_id),
            'is_request': notification_setting.is_request,
            'is_requisite': notification_setting.is_requisite,
            'is_order': notification_setting.is_order,
            'is_chat': notification_setting.is_chat,
            'is_transfer': notification_setting.is_transfer,
            'is_global': notification_setting.is_global,
            'is_active': notification_setting.is_active,
        }
