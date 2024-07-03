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


from typing import Optional

from app.db.models import Message, Session, Actions, OrderTypes, MessageUserPositions, NotificationTypes
from app.repositories import MessageRepository, OrderRepository, WalletAccountRepository, MessageFileRepository, \
    OrderFileRepository, FileKeyRepository
from app.services.action import ActionService
from app.services.base import BaseService
from app.services.file import FileService
from app.services.wallet import WalletService
from app.utils.bot.notification import BotNotification
from app.utils.decorators import session_required
from app.utils.exceptions import OrderNotPermission
from app.utils.websockets.chat import chat_connections_manager_fastapi
from config import settings


class MessageService(BaseService):
    model = Message

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        message = await MessageRepository().get_by_id(id_=id_)
        await WalletService().check_permission(
            account=account,
            wallets=[message.order.request.wallet, message.order.requisite.wallet],
            exception=OrderNotPermission(
                kwargs={
                    'field': 'Order',
                    'id_value': message.order.id,
                },
            ),
        )
        return {
            'message': await self.generate_message_dict(message=message),
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
            order_id: int,
    ) -> dict:
        account = session.account
        order = await OrderRepository().get_by_id(id_=order_id)
        await WalletService().check_permission(
            account=account,
            wallets=[order.request.wallet, order.requisite.wallet],
            exception=OrderNotPermission(
                kwargs={
                    'field': 'Order',
                    'id_value': order.id,
                },
            ),
        )
        messages = await MessageRepository().get_list(order_id=order_id)
        return {
            'messages': [
                await self.generate_message_dict(message=message)
                for message in messages
            ]
        }

    @session_required()
    async def chat(
            self,
            session: Session,
            order_id: int,
            role: Optional[str] = None,
            text: Optional[str] = None,
            files_key: Optional[str] = None,
    ):
        account = session.account
        order = await OrderRepository().get_by_id(id_=order_id)
        if not text and not await FileKeyRepository().get_list(key=files_key):
            return
        message = await MessageRepository().create(
            account=account,
            order=order,
            text=text,
            role=role,
        )
        await self.create_action(
            model=message,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'order_id': order.id,
                'text': text,
                'role': role,
                'files_key': files_key,
            }
        )
        if files_key:
            for file_key in await FileKeyRepository().get_list(key=files_key):
                if not file_key.file:
                    continue
                await OrderFileRepository().create_not_exists(order=order, file=file_key.file)
                await MessageFileRepository().create_not_exists(message=message, file=file_key.file)
        bot_notification = BotNotification()
        await bot_notification.send_notification_by_wallet(
            wallet=order.request.wallet,
            notification_type=NotificationTypes.CHAT,
            account_id_black_list=[account.id],
            text_key='notification_chat_new_message',
            order_id=order.id,
        )
        await bot_notification.send_notification_by_wallet(
            wallet=order.requisite.wallet,
            notification_type=NotificationTypes.CHAT,
            account_id_black_list=[account.id],
            text_key='notification_chat_new_message',
            order_id=order.id,
        )
        return await self.generate_message_dict(message=message)

    async def send_to_chat(
            self,
            token: str,
            order_id: int,
            role: str,
            text: str = None,
            files_key: str = None,
    ):
        message = await self.chat(token=token, order_id=order_id, text=text, role=role, files_key=files_key)
        await chat_connections_manager_fastapi.send(data=message, order_id=order_id)

    @staticmethod
    async def generate_message_dict(message: Message) -> Optional[dict]:
        if not message:
            return
        request_account = (await WalletAccountRepository().get(wallet=message.order.request.wallet)).account
        requisite_account = (await WalletAccountRepository().get(wallet=message.order.requisite.wallet)).account
        position = MessageUserPositions.UNKNOWN
        if message.order.type == OrderTypes.INPUT:
            if message.account.id == request_account.id:
                position = MessageUserPositions.SENDER
            elif message.account.id == requisite_account.id:
                position = MessageUserPositions.RECEIVER
        elif message.order.type == OrderTypes.OUTPUT:
            if message.account.id == request_account.id:
                position = MessageUserPositions.RECEIVER
            elif message.account.id == requisite_account.id:
                position = MessageUserPositions.SENDER
        action = await ActionService().get_action(model=message, action=Actions.CREATE)
        return {
            'id': message.id,
            'account': message.account.id,
            'role': message.role,
            'position': position,
            'order': message.order.id,
            'files': [
                await FileService().generate_file_dict(file=message_file.file)
                for message_file in await MessageFileRepository().get_list(message=message)
            ],
            'text': message.text,
            'date': action.datetime.strftime(settings.datetime_format),
        }
