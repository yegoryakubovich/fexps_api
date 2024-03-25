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

from app.db.models import Transfer, Session, Actions, TransferTypes, Account
from app.db.models.transfer import TransferOperations
from app.repositories import WalletAccountRepository
from app.repositories.transfer import TransferRepository
from app.repositories.wallet import WalletRepository
from app.services import ActionService
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.service_addons.transfer import create_transfer
from app.utils.service_addons.wallet import wallet_check_permission
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
        await wallet_check_permission(account=account, wallets=[wallet_from])
        wallet_to = await WalletRepository().get_by_id(id_=wallet_to_id)
        transfer = await create_transfer(
            type_=TransferTypes.PAYMENT,
            wallet_from=wallet_from,
            wallet_to=wallet_to,
            value=value
        )
        await self.create_action(
            model=transfer,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'id': transfer.id,
                'wallet_from_id': wallet_from.id,
                'wallet_to_id': wallet_to.id,
                'value': value
            },
        )
        return {'id': transfer.id}

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        transfer = await TransferRepository().get_by_id(id_=id_)
        await wallet_check_permission(
            account=account,
            wallets=[transfer.wallet_from, transfer.wallet_to],
        )
        return {
            'transfer': await self._generate_wallet_dict(account=account, transfer=transfer)
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
        await wallet_check_permission(account=account, wallets=[wallet])
        _transfers, results = await TransferRepository().search_by_wallet(
            wallet=wallet,
            is_sender=is_sender,
            is_receiver=is_receiver,
            page=page,
        )
        return {
            'transfers': [
                await self._generate_wallet_dict(account=account, transfer=transfer)
                for transfer in _transfers
            ],
            'results': results,
            'pages': ceil(results / settings.items_per_page),
            'page': page,
            'items_per_page': settings.items_per_page,
        }

    @staticmethod
    async def _generate_wallet_dict(account: Account, transfer: Transfer) -> dict:
        account_from = account_to = {
            'id': 0,
            'firstname': 'System',
            'lastname': '',
            'username': '',
            'short_name': f'System',
        }
        if not transfer.wallet_from.is_system:
            account_temp = (await WalletAccountRepository().get(wallet=transfer.wallet_from)).account
            account_from = {
                'id': account_temp.id,
                'firstname': account_temp.firstname,
                'lastname': account_temp.lastname,
                'username': account_temp.username,
                'short_name': f'{account_temp.firstname} {account_temp.lastname[0]}.',
            }
        if not transfer.wallet_to.is_system:
            account_temp = (await WalletAccountRepository().get(wallet=transfer.wallet_to)).account
            account_from = {
                'id': account_temp.id,
                'firstname': account_temp.firstname,
                'lastname': account_temp.lastname,
                'username': account_temp.username,
                'short_name': f'{account_temp.firstname} {account_temp.lastname[0]}.',
            }
        action = await ActionService().get_action(model=transfer, action=Actions.CREATE)
        operation = None
        if account_from['id'] == account.id:
            operation = TransferOperations.SEND
        elif account_to['id'] == account.id:
            operation = TransferOperations.RECEIVE
        return {
            'id': transfer.id,
            'type': transfer.type,
            'operation': operation,
            'wallet_from': transfer.wallet_from.id,
            'account_from': account_from,
            'wallet_to': transfer.wallet_to.id,
            'account_to': account_to,
            'value': transfer.value,
            'date': action.datetime.strftime(settings.datetime_format),
        }
