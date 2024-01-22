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


from app.db.models import Wallet, Session, WalletAccountRoles, Actions, CommissionPack
from app.repositories.base import DoesNotPermission
from app.repositories.commission_pack import CommissionPackRepository
from app.repositories.wallet import WalletRepository, WalletLimitReached
from app.repositories.wallet_account import WalletAccountRepository
from app.services.base import BaseService
from app.services.wallet_account import WalletAccountService
from app.utils.decorators import session_required
from config import WALLET_MAX_COUNT, WALLET_MAX_VALUE


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
            raise WalletLimitReached('Wallet limit reached.')
        commission_pack = await CommissionPackRepository().get(is_default=True)
        print(commission_pack)
        wallet = await WalletRepository().create(name=name, commission_pack=commission_pack)
        await self.create_action(
            model=wallet,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'name': name,
                'wallet_id': wallet.id,
                'commission_pack_id': commission_pack.id if commission_pack else None,
            },
        )
        await WalletAccountService().create(
            session=session,
            wallet_id=wallet.id,
            account_id=account.id,
        )

        return {'wallet_id': wallet.id}

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=id_)
        wallet_account = await WalletAccountRepository().get_by_account_and_wallet(account=account, wallet=wallet)
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
    async def update(
            self,
            session: Session,
            id_: int,
            name: str,
    ) -> dict:
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=id_)
        wallet_account = await WalletAccountRepository().get_by_account_and_wallet(account=account, wallet=wallet)
        await WalletRepository().update(
            wallet_account.wallet,
            name=name,
        )
        await self.create_action(
            model=wallet_account.wallet,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'id': id_,
                'wallet_account_id': wallet_account.id,
                'name': name,
            },
        )

        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=id_)
        wallet_account = await WalletAccountRepository().get_by_account_and_wallet(account=account, wallet=wallet)
        if wallet_account.role != WalletAccountRoles.OWNER:
            raise DoesNotPermission('You do not have sufficient rights to delete this wallet')
        await WalletRepository().delete(wallet_account.wallet)
        await self.create_action(
            model=wallet,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )
        await WalletAccountService().delete(
            session=session,
            id_=wallet_account.id,
        )

        return {}

    @staticmethod
    async def get_available_value(id_: int) -> float:  # FIXME
        wallet = await WalletRepository().get_by_id(id_=id_)
        result = WALLET_MAX_VALUE - wallet.value
        return result
