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


from typing import Optional, List

from app.db.models import Wallet, Session, WalletAccountRoles, Actions, Account
from app.repositories import CommissionPackRepository, AccountRepository, WalletRepository, WalletAccountRepository
from app.services.base import BaseService
from app.services.wallet_account import WalletAccountService
from app.utils import ApiException
from app.utils.decorators import session_required
from app.utils.exceptions import NotEnoughFundsOnBalance, WalletLimitReached
from app.utils.exceptions.wallet import WalletCountLimitReached, WalletPermissionError
from app.utils.value import value_to_float
from config import settings


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
        return {
            'id': wallet.id,
        }

    @session_required(permissions=['wallets'])
    async def get_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        wallet = await WalletRepository().get_by_id(id_=id_)
        return {
            'wallet': await self.generate_wallet_dict(wallet=wallet)
        }

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=id_)
        if not wallet.commission_pack:
            commission_pack = await CommissionPackRepository().get(is_default=True)
            if commission_pack:
                await WalletRepository().update(wallet, commission_pack=commission_pack)
        await self.check_permission(
            account=account,
            wallets=[wallet],
        )
        return {
            'wallet': await self.generate_wallet_dict(wallet=wallet)
        }

    @session_required(permissions=['wallets'])
    async def get_list_by_admin(
            self,
            session: Session,
            account_id: int = None,
    ) -> dict:
        if account_id:
            account = await AccountRepository().get_by_id(id_=account_id)
            result = {
                'wallets': [
                    await self.generate_wallet_dict(wallet=wallet_account.wallet)
                    for wallet_account in await WalletAccountRepository().get_list(account=account)
                ],
            }
        else:
            result = {
                'wallets': [
                    await self.generate_wallet_dict(wallet=wallet)
                    for wallet in await WalletRepository().get_list()
                ],
            }
        return result

    @session_required()
    async def get_list(
            self,
            session: Session,
    ) -> dict:
        account = session.account
        return {
            'wallets': [
                await self.generate_wallet_dict(wallet=wallet_account.wallet)
                for wallet_account in await WalletAccountRepository().get_list(account=account)
            ],
        }

    @session_required(permissions=['wallets'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            name: str = None,
            commission_pack_id: int = None,
    ):
        wallet = await WalletRepository().get_by_id(id_=id_)
        updates = {}
        action_parameters = {
            'updater': f'session_{session.id}',
            'id_': id_,
            'by_admin': True,
        }
        if name is not None:
            updates.update(name=name)
            action_parameters.update(name=name)
        if commission_pack_id is not None:
            commission_pack = await CommissionPackRepository().get_by_id(id_=commission_pack_id)
            updates.update(commission_pack=commission_pack)
            action_parameters.update(commission_pack_id=commission_pack_id)

        if updates:
            await WalletRepository().update(
                wallet,
                **updates,
            )
            await self.create_action(
                model=wallet,
                action=Actions.UPDATE,
                parameters=action_parameters,
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

    @session_required()
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
            },
        )
        await WalletAccountService().delete(
            session=session,
            id_=wallet_account.id,
        )
        return {}

    @staticmethod
    async def generate_wallet_dict(wallet: Wallet) -> Optional[dict]:
        if not wallet:
            return
        return {
            'id': wallet.id,
            'name': wallet.name,
            'commission_pack': wallet.commission_pack_id,
            'value': wallet.value,
            'value_banned': wallet.value_banned,
            'value_can_minus': wallet.value_can_minus,
            'system': wallet.is_system,
        }

    @staticmethod
    async def check_permission(
            account: Account,
            wallets: List[Wallet],
            exception: ApiException = WalletPermissionError(),
    ) -> Wallet:
        for wallet in wallets:
            if await WalletAccountRepository().get(account=account, wallet=wallet):
                return wallet
        raise exception

    @staticmethod
    async def check_balance(
            wallet: Wallet,
            value: int,
            error: bool = True,
    ) -> bool:
        """
        :param wallet: Wallet object
        :param value: int
        + if add value
        - if remove value
        :param error: bool
        Raised error
        :return:
        If error is True then return raise
        Else return True or False
        """
        current_value = wallet.value + value
        if current_value < -wallet.value_can_minus:
            if error:
                raise NotEnoughFundsOnBalance()
            return False
        if (current_value + wallet.value_banned) > settings.wallet_max_value:
            if error:
                raise WalletLimitReached(
                    kwargs={
                        'wallet_max_value': value_to_float(value=settings.wallet_max_value),
                    },
                )
            return False
        return True
