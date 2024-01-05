#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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


from app.db.models import Transfer, Session, Wallet
from app.repositories.base import DoesNotPermission
from app.repositories.transfer import NotEnoughFundsOnBalance, TransferRepository
from app.repositories.wallet import WalletRepository, WalletLimitReached
from app.repositories.wallet_account import WalletAccountRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from config import ITEMS_PER_PAGE, WALLET_MAX_VALUE


class TransferService(BaseService):
    model = Transfer

    @staticmethod
    async def transfer(
            wallet_from: Wallet,
            wallet_to: Wallet,
            value: float,
    ) -> Transfer:
        balance = wallet_from.value - wallet_from.value_banned - wallet_from.value_can_minus
        if value >= balance:
            raise NotEnoughFundsOnBalance("There are not enough funds on your balance")
        if (wallet_to.value + value) > WALLET_MAX_VALUE:
            raise WalletLimitReached(f"Transaction cannot be executed, max wallet value {WALLET_MAX_VALUE}")
        transfer = await TransferRepository().create(
            wallet_from=wallet_from,
            wallet_to=wallet_to,
            value=value
        )
        await WalletRepository().update(wallet_from, value=wallet_from.value - value)
        await WalletRepository().update(wallet_to, value=wallet_to.value + value)
        return transfer

    @session_required()
    async def create(
            self,
            session: Session,
            wallet_from_id: int,
            wallet_to_id: int,
            value,
    ) -> dict:
        account = session.account
        wallet_from = await WalletRepository().get_by_id(id_=wallet_from_id)
        if not await WalletAccountRepository().get(account=account, wallet=wallet_from):
            raise DoesNotPermission('You do not have sufficient rights to this wallet')
        await WalletAccountRepository().get_by_account_and_wallet(
            account=account,
            wallet=wallet_from
        )
        wallet_to = await WalletRepository().get_by_id(id_=wallet_to_id)

        transfer = await self.transfer(wallet_from=wallet_from, wallet_to=wallet_to, value=value)
        await self.create_action(
            model=transfer,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id': transfer.id,
                'wallet_from_id': wallet_from.id,
                'wallet_to_id': wallet_to.id,
                'value': value
            },
        )
        return {'transfer_id': transfer.id}

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        transfer = await TransferRepository().get_by_id(id_=id_)
        return {
            'transfer': {
                'id': transfer.id,
                'wallet_from': transfer.wallet_from.id,
                'wallet_to': transfer.wallet_to.id,
                'value': transfer.value,
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
        await WalletAccountRepository().get_by_account_and_wallet(account=account, wallet=wallet)
        transfers_db = await TransferRepository().search_by_wallet(
            wallet=wallet, is_sender=is_sender, is_receiver=is_receiver, page=page
        )
        transfers = {
            'transfers': [
                {
                    'id': transfer.id,
                    'wallet_from': transfer.wallet_from.id,
                    'wallet_to': transfer.wallet_to.id,
                    'value': transfer.value,
                }
                for transfer in transfers_db[0]
            ],
            'results': transfers_db[1],
            'page': page,
            'pages': transfers_db[2],
            'items_per_page': ITEMS_PER_PAGE,
        }
        return transfers
