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

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError

from app.db.models import Session, Actions, NotificationStates, NotificationTypes, \
    NotificationMethod, Method, Request
from app.repositories import NotificationMethodHistoryRepository, TextRepository, \
    NotificationMethodRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.value import value_replace, value_to_str, value_to_float
from config import settings


class NotificationMethodService(BaseService):
    model = NotificationMethod

    @staticmethod
    async def create(
            notification_method: NotificationMethod,
            request: Request,
            text_key: str,
            **kwargs,
    ):
        if not notification_method.telegram_id:
            return
        if not notification_method.is_active:
            return
        text = await TextRepository().get_by_key_or_none(key=text_key, language=notification_method.language)
        text = value_replace(text, **kwargs)
        notification_history = await NotificationMethodHistoryRepository().create(
            request=request,
            notification_method=notification_method,
            state=NotificationStates.WAIT,
            text=text,
        )
        await BaseService().create_action(
            model=notification_history,
            action=Actions.CREATE,
            parameters={
                'notification_method': notification_method.id,
                'telegram_id': notification_method.telegram_id,
                'state': NotificationStates.WAIT,
                'text_key': text_key,
                'language': notification_method.language.id_str,
                'text': text,
            },
        )

    @session_required(permissions=['notifications'], can_root=True)
    async def send_notification_by_task(self, session: Session):
        bot = Bot(token=settings.telegram_token)
        for notification_history in await NotificationMethodHistoryRepository().get_list(state=NotificationStates.WAIT):
            notification_method = notification_history.notification_method
            state = NotificationStates.SUCCESS
            error = None
            try:
                await bot.send_message(
                    chat_id=notification_method.telegram_id,
                    text=notification_history.text,
                    parse_mode=ParseMode.HTML,
                )
                await asyncio.sleep(0.2)
            except TelegramForbiddenError:
                state = NotificationStates.BLOCKED
            except Exception as e:
                error = e
                state = NotificationStates.ERROR
            await NotificationMethodHistoryRepository().update(notification_history, state=state)
            await self.create_action(
                model=notification_history,
                action=Actions.UPDATE,
                parameters={
                    'notification_method': notification_method.id,
                    'state': state,
                    'error': error,
                },
            )
        return {}

    async def create_notification_method_requisite_need_input(self, value: int, method: Method, request: Request):
        method_name = method.name_text.value_default
        currency = method.currency
        currency_name = currency.id_str.upper()
        value_str = value_to_str(
            value=value_to_float(value=value, decimal=currency.decimal),
        )
        for notification_method in await NotificationMethodRepository().get_list(method=method):
            if await NotificationMethodHistoryRepository().get(
                    notification_method=notification_method,
                    request=request,
            ):
                continue
            await self.create(
                notification_method=notification_method,
                request=request,
                text_key='notification_method_requisite_need_input',
                method=method_name,
                currency=currency_name,
                value=value_str,
            )

    async def create_notification_method_requisite_need_output(self, value: int, method: Method, request: Request):
        method_name = method.name_text.value_default
        currency = method.currency
        currency_name = currency.id_str.upper()
        value_str = value_to_str(
            value=value_to_float(value=value, decimal=currency.decimal),
        )
        for notification_method in await NotificationMethodRepository().get_list(method=method):
            if await NotificationMethodHistoryRepository().get(
                    notification_method=notification_method,
                    request=request,
            ):
                continue
            await self.create(
                notification_method=notification_method,
                request=request,
                text_key='notification_method_requisite_need_output',
                method=method_name,
                currency=currency_name,
                value=value_str,
            )
