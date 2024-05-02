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

from fastapi import UploadFile

from app.db.models import Message, Session, Actions, OrderTypes, MessageUserPositions
from app.repositories import MessageRepository, OrderRepository, WalletAccountRepository, FileRepository, \
    MessageFileRepository, OrderFileRepository
from app.services import ActionService, FileService
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import OrderNotPermission
from app.utils.service_addons.wallet import wallet_check_permission
from config import settings


class MessageService(BaseService):
    model = Message

    @session_required()
    async def chat(
            self,
            session: Session,
            order_id: int,
            text: Optional[str] = None,
            role: Optional[str] = None,
            files: Optional[list[UploadFile]] = None,
    ):
        account = session.account
        order = await OrderRepository().get_by_id(id_=order_id)
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
                'order_id': order_id,
                'text': text,
            }
        )
        for file in files:
            file = await FileService().create(session=session, file=file, return_model=True)
            await OrderFileRepository().create(order=order, file=file)
            await MessageFileRepository().create(message=message, file=file)
        return await self.generate_message_dict(message=message)

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
                await self.generate_message_dict(message=message)
                for message in messages
            ]
        }

    @staticmethod
    async def generate_message_dict(message: Message):
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
        files = []
        for message_file in await MessageFileRepository().get_list(message=message):
            with open(f'{settings.path_files}/{message_file.file.id_str}.{message_file.file.extension}', 'rb') as f:
                file_byte = f.read()
            files += [{
                'id_str': message_file.file.id_str,
                'filename': message_file.file.filename,
                'extension': message_file.file.extension,
                'url': f'{settings.get_file_url()}?id_str={message_file.file.id_str}',
                'value': file_byte.decode('ISO-8859-1'),
            }]
        return {
            'id': message.id,
            'account': message.account.id,
            'role': message.role,
            'position': position,
            'order': message.order.id,
            'files': files,
            'text': message.text,
            'date': action.datetime.strftime(settings.datetime_format),
        }
