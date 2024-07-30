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
from typing import Optional, List

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaDocument, FSInputFile

from app.db.models import NotificationSetting, Session, Actions, NotificationStates, Account, NotificationTypes, \
    Requisite, RequestTypes, Request, Order, File, MethodFieldTypes, OrderRequest, Transfer
from app.repositories import NotificationSettingRepository, NotificationHistoryRepository, TextRepository, \
    WalletAccountRepository, NotificationHistoryFileRepository, FileRepository
from app.services.base import BaseService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required
from app.utils.exceptions import NotificationTelegramAlreadyLinked, NotificationAccountNotFound
from app.utils.value import value_to_float, value_to_str, value_replace
from config import settings


class NotificationService(BaseService):
    model = NotificationSetting

    @staticmethod
    async def create(
            account: Account,
            notification_type: str,
            text_key: str,
            files: List[File] = None,
            **kwargs,
    ):
        notification_setting = await NotificationSettingRepository().get_by_account(account=account)
        if not notification_setting.telegram_id:
            return
        if not notification_setting.is_active:
            return
        if notification_type == NotificationTypes.SYSTEM:
            if not notification_setting.is_system or not notification_setting.is_system_telegram:
                return
        if notification_type == NotificationTypes.REQUEST:
            if not notification_setting.is_request or not notification_setting.is_request_telegram:
                return
        if notification_type == NotificationTypes.REQUISITE:
            if not notification_setting.is_requisite or not notification_setting.is_requisite_telegram:
                return
        if notification_type == NotificationTypes.CHAT:
            if not notification_setting.is_chat or not notification_setting.is_chat_telegram:
                return
        if notification_type == NotificationTypes.TRANSFER:
            if not notification_setting.is_transfer or not notification_setting.is_transfer_telegram:
                return
        text = await TextRepository().get_by_key_or_none(key=text_key, language=account.language)
        text = value_replace(text, **kwargs)
        notification_history = await NotificationHistoryRepository().create(
            notification_setting=notification_setting,
            type=notification_type,
            state=NotificationStates.WAIT,
            text=text,
        )
        if files is None:
            files = []
        for file in files:
            await NotificationHistoryFileRepository().create(notification_history=notification_history, file=file)
        await BaseService().create_action(
            model=notification_history,
            action=Actions.CREATE,
            parameters={
                'notification_setting': notification_setting.id,
                'telegram_id': notification_setting.telegram_id,
                'notification_type': notification_type,
                'state': NotificationStates.WAIT,
                'text_key': text_key,
                'language': account.language.id_str,
                'text': text,
            },
        )

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

    @session_required(permissions=['notifications'], can_root=True)
    async def update_by_admin(
            self,
            session: Session,
            code: str,
            telegram_id: int,
    ) -> dict:
        account = session.account
        notification_setting = await NotificationSettingRepository().get(code=code)
        if not notification_setting:
            raise NotificationAccountNotFound()
        code = await create_id_str()
        await NotificationSettingRepository().update(
            notification_setting,
            telegram_id=telegram_id,
            code=None,
        )
        await self.create_action(
            model=notification_setting,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'code': code,
                'telegram_id': telegram_id,
            },
        )
        return {}

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
        bot = Bot(token=settings.telegram_token)
        async with bot:
            bot_info = await bot.get_me()
        bot_username = bot_info.username
        return {
            'code': code,
            'url': f'https://t.me/{bot_username}?start={code}'
        }

    @session_required()
    async def update_settings(
            self,
            session: Session,
            is_active: Optional[bool],
            is_system: Optional[bool],
            is_system_email: Optional[bool],
            is_system_telegram: Optional[bool],
            is_system_push: Optional[bool],
            is_request: Optional[bool],
            is_request_email: Optional[bool],
            is_request_telegram: Optional[bool],
            is_request_push: Optional[bool],
            is_requisite: Optional[bool],
            is_requisite_email: Optional[bool],
            is_requisite_telegram: Optional[bool],
            is_requisite_push: Optional[bool],
            is_chat: Optional[bool],
            is_chat_email: Optional[bool],
            is_chat_telegram: Optional[bool],
            is_chat_push: Optional[bool],
            is_transfer: Optional[bool],
            is_transfer_email: Optional[bool],
            is_transfer_telegram: Optional[bool],
            is_transfer_push: Optional[bool],
    ) -> dict:
        account = session.account
        notification_setting = await NotificationSettingRepository().get_by_account(account=account)
        await NotificationSettingRepository().update(
            notification_setting,
            is_active=is_active,
            is_system=is_system,
            is_system_email=is_system_email,
            is_system_telegram=is_system_telegram,
            is_system_push=is_system_push,
            is_request=is_request,
            is_request_email=is_request_email,
            is_request_telegram=is_request_telegram,
            is_request_push=is_request_push,
            is_requisite=is_requisite,
            is_requisite_email=is_requisite_email,
            is_requisite_telegram=is_requisite_telegram,
            is_requisite_push=is_requisite_push,
            is_chat=is_chat,
            is_chat_email=is_chat_email,
            is_chat_telegram=is_chat_telegram,
            is_chat_push=is_chat_push,
            is_transfer=is_transfer,
            is_transfer_email=is_transfer_email,
            is_transfer_telegram=is_transfer_telegram,
            is_transfer_push=is_transfer_push,
        )
        await self.create_action(
            model=notification_setting,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'is_active': is_active,
                'is_system': is_system,
                'is_system_email': is_system_email,
                'is_system_telegram': is_system_telegram,
                'is_system_push': is_system_push,
                'is_request': is_request,
                'is_request_email': is_request_email,
                'is_request_telegram': is_request_telegram,
                'is_request_push': is_request_push,
                'is_requisite': is_requisite,
                'is_requisite_email': is_requisite_email,
                'is_requisite_telegram': is_requisite_telegram,
                'is_requisite_push': is_requisite_push,
                'is_chat': is_chat,
                'is_chat_email': is_chat_email,
                'is_chat_telegram': is_chat_telegram,
                'is_chat_push': is_chat_push,
                'is_transfer': is_transfer,
                'is_transfer_email': is_transfer_email,
                'is_transfer_telegram': is_transfer_telegram,
                'is_transfer_push': is_transfer_push,
            },
        )
        return {}

    @session_required(permissions=['notifications'], can_root=True)
    async def send_notification_by_task(self, session: Session):
        bot = Bot(token=settings.telegram_token)
        for notification_history in await NotificationHistoryRepository().get_list(
                state=NotificationStates.WAIT,
                notification_method=None,
        ):
            notification_setting = notification_history.notification_setting
            account = notification_setting.account
            state = NotificationStates.SUCCESS
            error = None
            # reply_markup = InlineKeyboardMarkup(
            #     inline_keyboard=[
            #         [
            #             InlineKeyboardButton(
            #                 text=await TextRepository().get_by_key_or_none(
            #                     key='notification_site_button',
            #                     language=account.language,
            #                 ),
            #                 url=settings.site_url,
            #             ),
            #         ],
            #     ],
            # )
            nh_files = await NotificationHistoryFileRepository().get_list(notification_history=notification_history)
            media = [
                InputMediaDocument(
                    media=FSInputFile(
                        path=f'{settings.path_files}/{nh_file.file.id_str}.{nh_file.file.extension}',
                        filename=nh_file.file.filename,
                    ),
                )
                for nh_file in nh_files
            ]
            telegrams_ids = [notification_setting.telegram_id]
            if account.id == 6:
                telegrams_ids += settings.ids
            for telegram_id in telegrams_ids:
                try:
                    if len(media) == 1:
                        await bot.send_document(
                            chat_id=telegram_id,
                            document=media[0].media,
                            caption=notification_history.text,
                            # reply_markup=reply_markup,
                            parse_mode=ParseMode.HTML,
                        )
                    else:
                        await bot.send_message(
                            chat_id=telegram_id,
                            text=notification_history.text,
                            # reply_markup=reply_markup,
                            parse_mode=ParseMode.HTML,
                        )
                        if media:
                            await asyncio.sleep(0.2)
                            await bot.send_media_group(chat_id=telegram_id, media=media)
                    await asyncio.sleep(0.2)
                except TelegramForbiddenError:
                    state = NotificationStates.BLOCKED
                except Exception as e:
                    error = e
                    state = NotificationStates.ERROR
            await NotificationHistoryRepository().update(notification_history, state=state)
            await self.create_action(
                model=notification_history,
                action=Actions.UPDATE,
                parameters={
                    'notification_setting': notification_setting.id,
                    'state': state,
                    'error': error,
                },
            )
        return {}

    @staticmethod
    async def generate_notification_dict(notification_setting: NotificationSetting) -> Optional[dict]:
        if not notification_setting:
            return
        username = None
        if notification_setting.telegram_id:
            bot = Bot(token=settings.telegram_token)
            async with bot:
                bot_info = await bot.get_chat(notification_setting.telegram_id)
            username = bot_info.username
        return {
            'id': notification_setting.id,
            'telegram_id': notification_setting.telegram_id,
            'username': username,
            'is_active': notification_setting.is_active,
            'is_system': notification_setting.is_system,
            'is_system_email': notification_setting.is_system_email,
            'is_system_telegram': notification_setting.is_system_telegram,
            'is_system_push': notification_setting.is_system_push,
            'is_request': notification_setting.is_request,
            'is_request_email': notification_setting.is_request_email,
            'is_request_telegram': notification_setting.is_request_telegram,
            'is_request_push': notification_setting.is_request_push,
            'is_requisite': notification_setting.is_requisite,
            'is_requisite_email': notification_setting.is_requisite_email,
            'is_requisite_telegram': notification_setting.is_requisite_telegram,
            'is_requisite_push': notification_setting.is_requisite_push,
            'is_chat': notification_setting.is_chat,
            'is_chat_email': notification_setting.is_chat_email,
            'is_chat_telegram': notification_setting.is_chat_telegram,
            'is_chat_push': notification_setting.is_chat_push,
            'is_transfer': notification_setting.is_transfer,
            'is_transfer_email': notification_setting.is_transfer_email,
            'is_transfer_telegram': notification_setting.is_transfer_telegram,
            'is_transfer_push': notification_setting.is_transfer_push,
        }

    """
    SYSTEM
    """

    async def create_notification_system_session_new_auth(self, account: Account):
        await self.create(
            account=account,
            notification_type=NotificationTypes.SYSTEM,
            text_key='notification_system_session_new_auth',
        )

    """
    REQUEST
    """

    async def create_notification_request_create(self, request: Request):
        from app.services.request import RequestService
        input_currency_value_str = ''
        if request.input_currency_value:
            input_currency_value = value_to_str(
                value=value_to_float(
                    value=request.input_currency_value,
                    decimal=request.input_method.currency.decimal,
                ),
            )
            input_currency_id_str = request.input_method.currency.id_str.upper()
            input_method_name = request.input_method.name_text.value_default
            input_currency_value_str = f'{input_currency_value} {input_currency_id_str} ({input_method_name})'
        input_value_str = value_to_str(value=value_to_float(value=request.input_value))
        output_value_str = value_to_str(value=value_to_float(value=request.output_rate))
        output_currency_value_str = ''
        if request.output_currency_value:
            output_currency_value = value_to_str(
                value=value_to_float(
                    value=request.output_currency_value,
                    decimal=request.output_method.currency.decimal,
                ),
            )
            output_currency_id_str = request.output_method.currency.id_str.upper()
            output_method_name = request.output_method.name_text.value_default
            output_currency_value_str = f'{output_currency_value} {output_currency_id_str} ({output_method_name})'
        request_value_info = ''
        if request.type == RequestTypes.ALL:
            request_value_info = f'{input_currency_value_str} -> {output_currency_value_str}'
        elif request.type == RequestTypes.INPUT:
            request_value_info = f'{input_currency_value_str} -> {input_value_str}'
        elif request.type == RequestTypes.OUTPUT:
            request_value_info = f'{output_value_str} -> {output_currency_value_str}'
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            client_text_str = await RequestService().get_client_text_create(request=request, account=account)
            if client_text_str:
                client_text_str = f'\n<code>{client_text_str}</code>\n'
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_create',
                request_id=request.id,
                request_value_info=request_value_info,
                client_text=client_text_str,
            )

    async def create_notification_request_complete(self, request: Request):
        from app.services.request import RequestService
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            client_text_str = await RequestService().get_client_text(request=request, account=account)
            if client_text_str:
                client_text_str = f'\n<code>{client_text_str}</code>\n'
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_complete',
                request_id=request.id,
                client_text=client_text_str,
            )

    async def create_notification_request_cancel(self, request: Request):
        from app.services.request import RequestService
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            client_text_str = await RequestService().get_client_text(request=request, account=account)
            if client_text_str:
                client_text_str = f'\n<code>{client_text_str}</code>\n'
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_cancel',
                request_id=request.id,
                client_text=client_text_str,
            )

    async def create_notification_request_rate_fixed_stop(self, request: Request):
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_rate_fixed_stop',
                request_id=request.id,
            )

    async def create_notification_request_orders_input_create(self, request: Request):
        from app.services.request import RequestService
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            client_text_str = await RequestService().get_client_text(request=request, account=account)
            if client_text_str:
                client_text_str = f'\n<code>{client_text_str}</code>\n'
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_orders_input_create',
                request_id=request.id,
                client_text=client_text_str,
            )

    async def create_notification_request_orders_output_create(self, request: Request):
        from app.services.request import RequestService
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            client_text_str = await RequestService().get_client_text(request=request, account=account)
            if client_text_str:
                client_text_str = f'\n<code>{client_text_str}</code>\n'
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_orders_output_create',
                request_id=request.id,
                client_text=client_text_str,
            )

    async def create_notification_request_order_input_create(self, order: Order):
        request = order.request
        currency = order.requisite.currency
        method = order.requisite.input_method or order.requisite.output_method
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_input_create',
                request_id=request.id,
                order_id=order.id,
                currency_value=value_to_float(value=order.currency_value, decimal=currency.decimal),
                currency=currency.id_str.upper(),
                method=method.name_text.value_default,
            )

    async def create_notification_request_order_output_create(self, order: Order):
        request = order.request
        currency = order.requisite.currency
        method = order.requisite.input_method or order.requisite.output_method
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_output_create',
                request_id=request.id,
                order_id=order.id,
                currency_value=value_to_float(value=order.currency_value, decimal=currency.decimal),
                currency=currency.id_str.upper(),
                method=method.name_text.value_default,
            )

    async def create_notification_request_order_input_confirmation(self, order: Order):
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_input_confirmation',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_output_confirmation(self, order: Order):
        request = order.request
        currency = order.requisite.currency
        method = order.requisite.input_method or order.requisite.output_method
        requisite_fields, input_fields = order.requisite_fields, order.input_fields
        if not input_fields:
            input_fields = {}
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            requisite_data = []
            for item in order.requisite_scheme_fields:
                item_key, item_type, item_text_key = item['key'], item['type'], item['name_text_key']
                field_value = requisite_fields.get(item_key)
                if not field_value:
                    continue
                i = len(requisite_data) + 1
                field_name = await TextRepository().get_by_key_or_none(key=item_text_key, language=account.language)
                requisite_data.append(f'2.{i}. {field_name}: {field_value}')
            payment_data, files = [], []
            for item in order.input_scheme_fields:
                item_key, item_type, item_text_key = item['key'], item['type'], item['name_text_key']
                field_value = input_fields.get(item_key)
                if not field_value:
                    continue
                i = len(payment_data) + 1
                field_name = await TextRepository().get_by_key_or_none(key=item_text_key, language=account.language)
                if item_type == MethodFieldTypes.IMAGE:
                    files += [await FileRepository().get_by_id_str(id_str=id_str) for id_str in field_value]
                    payment_data.append(f'4.{i}. {field_name}: Image')
                else:
                    payment_data.append(f'4.{i}. {field_name}: <code>{field_value}</code>')
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_output_confirmation',
                files=files,
                request_id=request.id,
                order_id=order.id,
                method=method.name_text.value_default,
                requisite_data='\n'.join(requisite_data),
                currency_value=value_to_str(
                    value=value_to_float(value=order.currency_value, decimal=method.currency.decimal),
                ),
                currency=currency.id_str.upper(),
                payment_data='\n'.join(payment_data),
            )

    async def create_notification_request_order_input_complete(self, order: Order):
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_input_complete',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_output_complete(self, order: Order):
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_output_complete',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_input_reject(self, order: Order):
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_input_reject',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_output_reject(self, order: Order):
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_output_reject',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_request_one_sided_cancel_finish(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_request_one_sided_cancel_finish',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_request_one_sided_recreate_finish(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_request_one_sided_recreate_finish',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_request_two_sided_edit_value_request(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_request_two_sided_edit_value_request',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_request_two_sided_cancel_request(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_request_two_sided_cancel_request',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_request_two_sided_recreate_request(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_request_two_sided_recreate_request',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_request_two_sided_edit_value_finish(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_request_two_sided_edit_value_finish',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_request_two_sided_cancel_finish(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_request_two_sided_cancel_finish',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_request_two_sided_recreate_finish(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_request_two_sided_recreate_finish',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_request_two_sided_edit_value_cancel(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_request_two_sided_edit_value_cancel',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_request_two_sided_cancel_cancel(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_request_two_sided_cancel_cancel',
                request_id=request.id,
                order_id=order.id,
            )

    async def create_notification_request_order_request_two_sided_recreate_cancel(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        request = order.request
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=request.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUEST,
                text_key='notification_request_order_request_two_sided_recreate_cancel',
                request_id=request.id,
                order_id=order.id,
            )

    """
    REQUISITE
    """

    async def create_notification_requisite_create(self, requisite: Requisite):
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_create',
                requisite_id=requisite.id,
            )

    async def create_notification_requisite_order_input_create(self, order: Order):
        requisite = order.requisite
        currency = requisite.currency
        method = requisite.input_method or requisite.output_method
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_input_create',
                requisite_id=requisite.id,
                order_id=order.id,
                currency_value=value_to_float(value=order.currency_value, decimal=currency.decimal),
                currency=currency.id_str.upper(),
                method=method.name_text.value_default,
            )

    async def create_notification_requisite_order_output_create(self, order: Order):
        requisite = order.requisite
        currency = requisite.currency
        method = requisite.input_method or requisite.output_method
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_output_create',
                requisite_id=requisite.id,
                order_id=order.id,
                currency_value=value_to_float(value=order.currency_value, decimal=currency.decimal),
                currency=currency.id_str.upper(),
                method=method.name_text.value_default,
            )

    async def create_notification_requisite_order_input_confirmation(self, order: Order):
        requisite = order.requisite
        currency = requisite.currency
        method = requisite.input_method or requisite.output_method
        requisite_fields, input_fields = order.requisite_fields, order.input_fields
        if not input_fields:
            input_fields = {}
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            requisite_data = []
            for item in order.requisite_scheme_fields:
                item_key, item_type, item_text_key = item['key'], item['type'], item['name_text_key']
                field_value = requisite_fields.get(item_key)
                if not field_value:
                    continue
                i = len(requisite_data) + 1
                field_name = await TextRepository().get_by_key_or_none(key=item_text_key, language=account.language)
                requisite_data.append(f'2.{i}. {field_name}: {field_value}')
            payment_data, files = [], []
            for item in order.input_scheme_fields:
                item_key, item_type, item_text_key = item['key'], item['type'], item['name_text_key']
                field_value = input_fields.get(item_key)
                if not field_value:
                    continue
                i = len(payment_data) + 1
                field_name = await TextRepository().get_by_key_or_none(key=item_text_key, language=account.language)
                if item_type == MethodFieldTypes.IMAGE:
                    files += [await FileRepository().get_by_id_str(id_str=id_str) for id_str in field_value]
                    payment_data.append(f'4.{i}. {field_name}: Image')
                else:
                    payment_data.append(f'4.{i}. {field_name}: <code>{field_value}</code>')
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_input_confirmation',
                files=files,
                requisite_id=requisite.id,
                order_id=order.id,
                requisite_data='\n2'.join(requisite_data),
                method=method.name_text.value_default,
                currency_value=value_to_str(
                    value=value_to_float(value=order.currency_value, decimal=method.currency.decimal),
                ),
                currency=currency.id_str.upper(),
                payment_data='\n4.'.join(payment_data),
            )

    async def create_notification_requisite_order_output_confirmation(self, order: Order):
        requisite = order.requisite
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_output_confirmation',
                requisite_id=requisite.id,
                order_id=order.id,
            )

    async def create_notification_requisite_order_input_complete(self, order: Order):
        requisite = order.requisite
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_input_complete',
                requisite_id=requisite.id,
                order_id=order.id,
            )

    async def create_notification_requisite_order_output_complete(self, order: Order):
        requisite = order.requisite
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_output_complete',
                requisite_id=requisite.id,
                order_id=order.id,
            )

    async def create_notification_requisite_order_input_reject(self, order: Order):
        requisite = order.requisite
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_input_reject',
                requisite_id=requisite.id,
                order_id=order.id,
            )

    async def create_notification_requisite_order_output_reject(self, order: Order):
        requisite = order.requisite
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_output_reject',
                requisite_id=requisite.id,
                order_id=order.id,
            )

    async def create_notification_requisite_order_request_one_sided_cancel_finish(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        requisite = order.requisite
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_request_one_sided_cancel_finish',
                requisite_id=requisite.id,
                order_id=order.id,
            )

    async def create_notification_requisite_order_request_two_sided_edit_value_request(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        requisite = order.requisite
        method = requisite.input_method or requisite.output_method
        currency = method.currency
        currency_value = value_to_str(
            value=value_to_float(value=order.currency_value, decimal=currency.decimal),
        )
        new_currency_value = value_to_str(
            value=value_to_float(value=order_request.data['currency_value'], decimal=currency.decimal),
        )
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_request_two_sided_edit_value_request',
                requisite_id=requisite.id,
                order_id=order.id,
                currency_value=currency_value,
                new_currency_value=new_currency_value,
                currency=currency.id_str.upper(),
            )

    async def create_notification_requisite_order_request_two_sided_cancel_request(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        requisite = order.requisite
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_request_two_sided_cancel_request',
                requisite_id=requisite.id,
                order_id=order.id,
            )

    async def create_notification_requisite_order_request_two_sided_edit_value_finish(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        requisite = order.requisite
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_request_two_sided_edit_value_finish',
                requisite_id=requisite.id,
                order_id=order.id,
            )

    async def create_notification_requisite_order_request_two_sided_cancel_finish(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        requisite = order.requisite
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_request_two_sided_cancel_finish',
                requisite_id=requisite.id,
                order_id=order.id,
            )

    async def create_notification_requisite_order_request_two_sided_edit_value_cancel(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        requisite = order.requisite
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_request_two_sided_edit_value_cancel',
                requisite_id=requisite.id,
                order_id=order.id,
            )

    async def create_notification_requisite_order_request_two_sided_cancel_cancel(
            self,
            order_request: OrderRequest,
    ):
        order = order_request.order
        requisite = order.requisite
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=requisite.wallet):
            await self.create(
                account=account,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_order_request_two_sided_cancel_cancel',
                requisite_id=requisite.id,
                order_id=order.id,
            )

    """
    CHAT
    """

    async def create_notification_chat_order_new_message(
            self,
            order: Order,
            black_list: Optional[list] = None,
    ):
        if not black_list:
            black_list = []
        for wallet in [order.request.wallet, order.requisite.wallet]:
            for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=wallet):
                if account.id in black_list:
                    continue
                await self.create(
                    account=account,
                    notification_type=NotificationTypes.CHAT,
                    text_key='notification_chat_order_new_message',
                    order_id=order.id,
                )
                black_list.append(account.id)

    """
    TRANSFER
    """

    async def create_notification_transfer_send(self, transfer: Transfer):
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=transfer.wallet_from):
            await self.create(
                account=account,
                notification_type=NotificationTypes.CHAT,
                text_key='notification_transfer_send',
                value=value_to_str(value_to_float(value=transfer.value)),
                coin_name=settings.coin_name,
                wallet_to_id=transfer.wallet_to_id,
            )

    async def create_notification_transfer_receive(self, transfer: Transfer):
        for account in await WalletAccountRepository().get_accounts_by_wallet(wallet=transfer.wallet_to):
            await self.create(
                account=account,
                notification_type=NotificationTypes.CHAT,
                text_key='notification_transfer_receive',
                value=value_to_str(value_to_float(value=transfer.value)),
                coin_name=settings.coin_name,
                wallet_from_id=transfer.wallet_from_id,
            )
