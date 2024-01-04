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


from app.db.models import Wallet, Session, WalletAccountRoles
from app.repositories.wallet import WalletRepository, WalletLimitReached
from app.repositories.wallet_account import WalletAccountRepository
from app.services import WalletAccountService
from app.services.base import BaseService
from app.utils.decorators import session_required
from config import WALLET_MAX_COUNT


class WalletService(BaseService):
    model = Wallet

    @session_required()
    async def create(
            self,
            session: Session,
            name: str,
    ) -> dict:
        account = session.account
        wallet_account_list = await WalletAccountRepository().get_list(account=account, role=WalletAccountRoles.OWNER)
        if len(wallet_account_list) >= WALLET_MAX_COUNT:
            raise WalletLimitReached("Wallet limit reached.")
        wallet = await WalletRepository().create(name=name)
        await self.create_action(
            model=wallet,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'name': name,
                'wallet_id': wallet.id,
            },
        )
        await WalletAccountService().create(session=session, wallet=wallet)

        return {'wallet_id': wallet.id}

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        wallet_account = await WalletAccountRepository().get_by_account_and_id(account=account, id_=id_)

        return {
            'wallet': {
                'id': wallet_account.wallet.id,
                'name': wallet_account.wallet.name,
                'value': wallet_account.wallet.value,
                'value_banned': wallet_account.wallet.value_banned,
                'value_can_minus': wallet_account.wallet.value_can_minus,
            }
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
    ) -> dict:
        account = session.account
        wallets = {
            'wallets': [
                {
                    'id': wallet_account.wallet.id,
                    'name': wallet_account.wallet.name,
                    'value': wallet_account.wallet.value,
                    'value_banned': wallet_account.wallet.value_banned,
                    'value_can_minus': wallet_account.wallet.value_can_minus,
                }
                for wallet_account in await WalletAccountRepository().get_list(account=account)
            ],
        }

        return wallets

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        wallet_account = await WalletAccountRepository().get_by_account_and_id(account=account, id_=id_)
        await WalletRepository().delete(wallet_account.wallet)
        await WalletAccountRepository().delete(wallet_account)
        await self.create_action(
            model=wallet_account.wallet,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
                'wallet_account_id': wallet_account.id
            },
        )

        return {}

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            name: str,
    ) -> dict:
        account = session.account
        wallet_account = await WalletAccountRepository().get_by_account_and_id(account=account, id_=id_)
        await WalletRepository().update(
            wallet_account.wallet,
            name=name,
        )
        await self.create_action(
            model=wallet_account.wallet,
            action='update',
            parameters={
                'updater': f'session_{session.id}',
                'id': id_,
                'wallet_account_id': wallet_account.id,
                'name': name,
            },
        )

        return {}
