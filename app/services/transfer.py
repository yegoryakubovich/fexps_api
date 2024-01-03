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
from app.repositories.transfer import NotEnoughFundsOnBalance, TransferRepository, ValueMustBePositive
from app.repositories.wallet import WalletRepository
from app.repositories.wallet_account import WalletAccountRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


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
        print("HELLO")
        123
        wallet_account_from = await WalletAccountRepository().get_by_account_and_id(account=account, id_=wallet_from_id)
        wallet_from: Wallet = wallet_account_from.wallet
        wallet_to = await WalletRepository().get_by_id(id_=wallet_to_id)

        if value <= 0:
            raise ValueMustBePositive("The value must be positive")
        balance = wallet_from.value - wallet_from.value_banned - wallet_from.value_can_minus
        if value > balance:
            raise NotEnoughFundsOnBalance("There are not enough funds on your balance")

        transfer = await TransferRepository().create(
            wallet_from=wallet_from,
            wallet_to=wallet_to,
            value=value
        )
        await WalletRepository().update(
            wallet_from,
            value=wallet_from.value - value
        )
        await WalletRepository().update(
            wallet_to,
            value=wallet_to.value + value
        )

        await self.create_action(
            model=transfer,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'wallet_from_id': f'{wallet_from.id}',
                'wallet_to_id': f'{wallet_to.id}',
                'value': f'{value}'
            },
        )

        return {'transfer_id': transfer.id}

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        transfer = await WalletAccountRepository().get_by_account_and_id(account=account, id_=id_)

        return {
            'transfer': {
                'id': transfer.id,
                'wallet_from': transfer.wallet_from.id,
                'wallet_to': transfer.wallet_to.id,
                'value': transfer.value,
            }
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
    ) -> dict:
        account = session.account
        transfers = {
            'transfers': [
                {
                    'id': transfer.id,
                    'wallet_from': transfer.wallet_from.id,
                    'wallet_to': transfer.wallet_to.id,
                    'value': transfer.value,
                }
                for transfer in await TransferRepository().get_list(account=account)
            ],
        }

        return transfers
