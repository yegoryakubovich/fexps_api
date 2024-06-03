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
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.db.models import NotificationStates, Account, NotificationTypes, Actions, Language, Wallet
from app.repositories import NotificationSettingRepository, NotificationHistoryRepository, WalletAccountRepository, \
    TextRepository, TextTranslationRepository
from app.services.base import BaseService
from config import settings


class BotNotification:

    def __init__(self):
        self.bot = Bot(token=settings.telegram_token)

    @staticmethod
    async def get_text(
            key: str,
            language: Language,
            **kwargs
    ) -> str:
        text = await TextRepository().get(key=key)
        if not text:
            return f'404 {key}'
        translation = await TextTranslationRepository().get(text=text, language=language)
        if not translation:
            return text.value_default.format(**kwargs)
        return translation.value.format(**kwargs)

    async def send_notification_by_wallet(
            self,
            wallet: Wallet,
            notification_type: str,
            text_key: str,
            account_id_black_list: list[int] = None,
            **kwargs,
    ):
        if not account_id_black_list:
            account_id_black_list = []
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=wallet):
            if account.id in account_id_black_list:
                continue
            await self.send_notification(
                account=account,
                notification_type=notification_type,
                text_key=text_key,
                **kwargs,
            )
            await asyncio.sleep(0.5)

    async def send_notification(
            self,
            account: Account,
            notification_type: str,
            text_key: str,
            **kwargs,
    ):
        notification_setting = await NotificationSettingRepository().get(account=account)
        if not notification_setting.telegram_id:
            return
        if not notification_setting.is_active:
            return
        if notification_type == NotificationTypes.REQUEST and not notification_setting.is_request:
            return
        if notification_type == NotificationTypes.REQUISITE and not notification_setting.is_requisite:
            return
        if notification_type == NotificationTypes.ORDER and not notification_setting.is_order:
            return
        if notification_type == NotificationTypes.CHAT and not notification_setting.is_chat:
            return
        if notification_type == NotificationTypes.TRANSFER and not notification_setting.is_transfer:
            return
        if notification_type == NotificationTypes.GLOBAL and not notification_setting.is_global:
            return
        state = NotificationStates.SUCCESS
        text = await self.get_text(key=text_key, language=account.language, **kwargs)
        try:
            await self.bot.send_message(
                chat_id=notification_setting.telegram_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=await self.get_text(key='notification_site_button', language=account.language),
                                url=settings.site_url,
                            ),
                        ],
                    ],
                ),
            )
        except TelegramForbiddenError:
            state = NotificationStates.BLOCKED
        except Exception as e:
            logging.critical(e)
            state = NotificationStates.ERROR
        notification_history = await NotificationHistoryRepository().create(
            notification_setting=notification_setting,
            type=notification_type,
            state=state,
            text=text,
        )
        await BaseService().create_action(
            model=notification_history,
            action=Actions.CREATE,
            parameters={
                'notification_setting': notification_setting.id,
                'telegram_id': notification_setting.telegram_id,
                'notification_type': notification_type,
                'state': state,
                'text_key': text_key,
                'text': text,
            },
        )
