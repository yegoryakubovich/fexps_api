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

from app.db.models import Transfer, Session, Actions, TransferTypes
from app.db.models.transfer import TransferOperations
from app.repositories.transfer import TransferRepository
from app.repositories.wallet import WalletRepository
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
            'transfer': {
                'id': transfer.id,
                'wallet_from': transfer.wallet_from.id,
                'wallet_to': transfer.wallet_to.id,
                'value': transfer.value,
                'date': transfer.date.strftime(settings.datetime_format),
            }
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
        transfers = []
        for transfer in _transfers:
            operation = TransferOperations.SEND if transfer.wallet_from.id == wallet.id else TransferOperations.RECEIVE
            transfers.append(
                {
                    'id': transfer.id,
                    'type': transfer.type,
                    'operation': operation,
                    'wallet_from': transfer.wallet_from.id,
                    'wallet_to': transfer.wallet_to.id,
                    'value': transfer.value,
                    'date': transfer.date.strftime(settings.datetime_format),
                }
            )
        return {
            'transfers': transfers,
            'results': results,
            'pages': ceil(results / settings.items_per_page),
            'page': page,
            'items_per_page': settings.items_per_page,
        }
