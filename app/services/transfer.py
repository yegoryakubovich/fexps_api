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


from math import ceil
from typing import Optional

from app.db.models import Transfer, Session, Actions, TransferTypes, Wallet, NotificationTypes, Order
from app.db.models.transfer import TransferOperations
from app.repositories import WalletAccountRepository, OrderTransferRepository, TransferRepository, WalletRepository
from app.services.action import ActionService
from app.services.base import BaseService
from app.services.notification import NotificationService
from app.services.wallet import WalletService
from app.utils.decorators import session_required
from app.utils.value import value_to_float
from config import settings


class TransactionTypes:
    send = 'send'
    receive = 'receive'


class TransferService(BaseService):
    model = Transfer

    @session_required()
    async def create(
            self,
            session: Session,
            wallet_from_id: int,
            wallet_to_id: int,
            value: int,
    ) -> dict:
        account = session.account
        wallet_from = await WalletRepository().get_by_id(id_=wallet_from_id)
        await WalletService().check_permission(
            account=account,
            wallets=[wallet_from],
        )
        wallet_to = await WalletRepository().get_by_id(id_=wallet_to_id)
        transfer = await self.create_transfer(
            type_=TransferTypes.PAYMENT,
            wallet_from=wallet_from,
            wallet_to=wallet_to,
            value=value
        )
        await NotificationService().create_notification_by_wallet(
            wallet=wallet_to,
            notification_type=NotificationTypes.TRANSFER,
            text_key='notification_transfer_create',
            value=value_to_float(value=value),
            wallet_to_id=wallet_to_id,
            wallet_from_id=wallet_from_id,
        )
        await NotificationService().create_notification_by_wallet(
            wallet=wallet_from,
            notification_type=NotificationTypes.TRANSFER,
            text_key='notification_transfer_create',
            value=value_to_float(value=value),
            wallet_to_id=wallet_to_id,
            wallet_from_id=wallet_from_id,
        )
        return {
            'id': transfer.id,
        }

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        transfer = await TransferRepository().get_by_id(id_=id_)
        wallet = await WalletService().check_permission(
            account=account,
            wallets=[transfer.wallet_from, transfer.wallet_to],
        )
        return {
            'transfer': await self.generate_transfer_dict(wallet=wallet, transfer=transfer)
        }

    @session_required()
    async def search(
            self,
            session: Session,
            wallet_id: int,
            is_sender: bool,
            is_receiver: bool,
            page: int,
    ) -> dict:
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        await WalletService().check_permission(
            account=account,
            wallets=[wallet],
        )
        _transfers, results = await TransferRepository().search_by_wallet(
            wallet=wallet,
            is_sender=is_sender,
            is_receiver=is_receiver,
            page=page,
        )
        return {
            'transfers': [
                await self.generate_transfer_dict(wallet=wallet, transfer=transfer)
                for transfer in _transfers
            ],
            'results': results,
            'pages': ceil(results / settings.items_per_page),
            'page': page,
            'items_per_page': settings.items_per_page,
        }

    @staticmethod
    async def generate_transfer_dict(transfer: Transfer, wallet: Wallet) -> Optional[dict]:
        if not transfer:
            return
        if transfer.wallet_from.is_system:
            account_from = {'id': 0, 'firstname': 'System', 'lastname': '', 'username': '', 'short_name': f'System'}
        else:
            wallet_account_from = await WalletAccountRepository().get(wallet=transfer.wallet_from)
            _account_from = wallet_account_from.account
            account_from = {
                'id': _account_from.id,
                'firstname': _account_from.firstname,
                'lastname': _account_from.lastname,
                'username': _account_from.username,
                'short_name': f'{_account_from.firstname} {_account_from.lastname[0]}.'.title(),
            }
        if transfer.wallet_to.is_system:
            account_to = {'id': 0, 'firstname': 'System', 'lastname': '', 'username': '', 'short_name': f'System'}
        else:
            wallet_account_to = await WalletAccountRepository().get(wallet_id=transfer.wallet_to_id)
            _account_to = wallet_account_to.account
            account_to = {
                'id': _account_to.id,
                'firstname': _account_to.firstname,
                'lastname': _account_to.lastname,
                'username': _account_to.username,
                'short_name': f'{_account_to.firstname} {_account_to.lastname[0]}.'.title(),
            }
        action = await ActionService().get_action(model=transfer, action=Actions.CREATE)
        order = await OrderTransferRepository().get(transfer=transfer)
        operation = TransferOperations.SEND if transfer.wallet_from_id == wallet.id else TransferOperations.RECEIVE
        return {
            'id': transfer.id,
            'type': transfer.type,
            'operation': operation,
            'wallet_from': transfer.wallet_from.id,
            'account_from': account_from,
            'wallet_to': transfer.wallet_to.id,
            'account_to': account_to,
            'order': order.id if order else None,
            'value': transfer.value,
            'date': action.datetime.strftime(settings.datetime_format),
        }

    @staticmethod
    async def create_transfer(
            type_: str,
            wallet_from: Wallet,
            wallet_to: Wallet,
            value: int,
            order: Order = None,
            ignore_bal: bool = False,
    ) -> Transfer:
        wallet_from = await WalletRepository().get_by_id(id_=wallet_from.id)
        wallet_to = await WalletRepository().get_by_id(id_=wallet_to.id)
        if value < 0:
            value = -value
            wallet_from, wallet_to = wallet_to, wallet_from
        if not ignore_bal:
            await WalletService().check_balance(wallet=wallet_from, value=-value)
            await WalletService().check_balance(wallet=wallet_to, value=value)
        await WalletRepository().update(wallet_from, value=wallet_from.value - value)
        transfer = await TransferRepository().create(
            type=type_,
            wallet_from=wallet_from,
            wallet_to=wallet_to,
            value=value,
        )
        if order:
            await OrderTransferRepository().create(order=order, transfer=transfer)
        await WalletRepository().update(wallet_to, value=wallet_to.value + value)
        await BaseService().create_action(
            model=transfer,
            action=Actions.CREATE,
            parameters={
                'id': transfer.id,
                'type': type_,
                'wallet_from_id': wallet_from.id,
                'wallet_to_id': wallet_to.id,
                'value': value,
                'order': order,
                'ignore_bal': ignore_bal,
            },
        )
        return transfer
