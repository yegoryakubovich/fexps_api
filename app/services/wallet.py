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


from typing import List

from app.db.models import Wallet, Session, WalletAccountRoles, Actions, Account
from app.repositories.commission_pack import CommissionPackRepository
from app.repositories.wallet import WalletRepository
from app.repositories.wallet_account import WalletAccountRepository
from app.services.base import BaseService
from app.services.wallet_account import WalletAccountService
from app.utils import ApiException
from app.utils.decorators import session_required
from app.utils.exceptions.wallet import WalletCountLimitReached, WalletPermissionError
from config import settings


class WalletService(BaseService):
    model = Wallet

    @session_required(permissions=['wallets'])
    async def create(
            self,
            session: Session,
            name: str,
    ) -> dict:
        account = session.account
        wallet_account_list = await WalletAccountRepository().get_list(account=account, role=WalletAccountRoles.OWNER)
        if len(wallet_account_list) >= settings.wallet_max_count:
            raise WalletCountLimitReached()
        commission_pack = await CommissionPackRepository().get(is_default=True)
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
        )

        return {'wallet_id': wallet.id}

    @session_required(permissions=['wallets'])
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=id_)
        wallet_account = await WalletAccountRepository().get(account=account, wallet=wallet)
        if not wallet_account:
            raise WalletPermissionError()
        return {
            'wallet': {
                'id': wallet_account.wallet.id,
                'name': wallet_account.wallet.name,
                'value': wallet_account.wallet.value,
                'value_banned': wallet_account.wallet.value_banned,
                'value_can_minus': wallet_account.wallet.value_can_minus,
            }
        }

    @session_required(permissions=['wallets'])
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

    @session_required(permissions=['wallets'])
    async def update(
            self,
            session: Session,
            id_: int,
            name: str,
    ) -> dict:
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=id_)
        wallet_account = await WalletAccountRepository().get(account=account, wallet=wallet)
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

    @session_required(permissions=['wallets'])
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=id_)
        wallet_account = await WalletAccountRepository().get(account=account, wallet=wallet)
        if wallet_account.role != WalletAccountRoles.OWNER:
            raise WalletPermissionError()
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
    async def get_available_value(wallet: Wallet) -> float:  # FIXME
        return settings.wallet_max_value - wallet.value

    @staticmethod
    async def get_free_value(wallet: Wallet):
        return wallet.value - wallet.value_can_minus

    @staticmethod
    async def check_permission(
            account: Account,
            wallets: List[Wallet],
            exception: ApiException = WalletPermissionError(),
    ) -> None:
        permission = False
        for wallet in wallets:
            if await WalletAccountRepository().get(account=account, wallet=wallet):
                permission = True
        if not permission:
            raise exception
