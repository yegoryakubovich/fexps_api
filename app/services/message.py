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

from app.db.models import Message, Session, Actions, OrderTypes
from app.repositories import MessageRepository, OrderRepository, WalletAccountRepository, ImageRepository
from app.services import ActionService
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import OrderNotPermission
from app.utils.service_addons.wallet import wallet_check_permission
from config import settings


class AccountPosition:
    UNKNOWN = 'unknown'
    SENDER = 'sender'
    RECEIVER = 'receiver'


class MessageService(BaseService):
    model = Message

    @session_required()
    async def chat(
            self,
            session: Session,
            order_id: int,
            image_id_str: Optional[str] = None,
            text: Optional[str] = None,
    ):
        account = session.account
        order = await OrderRepository().get_by_id(id_=order_id)
        image = None
        if image_id_str:
            image = await ImageRepository().get_by_id_str(id_str=image_id_str)
        message = await MessageRepository().create(
            account=account,
            order=order,
            image=image,
            text=text,
        )
        await self.create_action(
            model=message,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'order_id': order_id,
                'image': image,
                'text': text,
            }
        )
        return await self._generate_message_dict(message=message)

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        message = await MessageRepository().get_by_id(id_=id_)
        await wallet_check_permission(
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
            'message': await self._generate_message_dict(message=message),
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
            order_id: int,
    ) -> dict:
        account = session.account
        order = await OrderRepository().get_by_id(id_=order_id)
        await wallet_check_permission(
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
                await self._generate_message_dict(message=message)
                for message in messages
            ]
        }

    @staticmethod
    async def _generate_message_dict(message: Message):
        request_account = (await WalletAccountRepository().get(wallet=message.order.request.wallet)).account
        requisite_account = (await WalletAccountRepository().get(wallet=message.order.requisite.wallet)).account
        position = AccountPosition.UNKNOWN
        if message.order.type == OrderTypes.INPUT:
            if message.account.id == request_account.id:
                position = AccountPosition.SENDER
            elif message.account.id == requisite_account.id:
                position = AccountPosition.RECEIVER
        elif message.order.type == OrderTypes.OUTPUT:
            if message.account.id == request_account.id:
                position = AccountPosition.RECEIVER
            elif message.account.id == requisite_account.id:
                position = AccountPosition.SENDER
        action = await ActionService().get_action(model=message, action=Actions.CREATE)
        image_id_str = None
        if message.image:
            image_id_str = message.image.id_str
        return {
            'id': message.id,
            'account': message.account.id,
            'account_position': position,
            'order': message.order.id,
            'image': image_id_str,
            'text': message.text,
            'date': action.datetime.strftime(settings.datetime_format),
        }
