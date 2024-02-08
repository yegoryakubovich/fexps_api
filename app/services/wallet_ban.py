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


from app.db.models import Session, Actions, WalletBan, Wallet
from app.repositories.wallet import WalletRepository
from app.repositories.wallet_ban import WalletBanRepository
from app.services.base import BaseService
from app.services.wallet import WalletService
from app.utils.decorators import session_required
from app.utils.exceptions.wallet import NotEnoughFundsOnBalance, WalletLimitReached
from config import settings


class WalletBanService(BaseService):
    model = WalletBan

    @session_required(permissions=['wallets_bans'])
    async def create(
            self,
            session: Session,
            wallet_id: int,
            value: int,
            reason: str,
    ) -> dict:
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        wallet_ban = await self.create_related(wallet=wallet, value=value, reason=reason)
        await self.create_action(
            model=wallet_ban,
            action=Actions.CREATE,
            parameters={
                'deleter': f'session_{session.id}',
                'wallet_id': wallet_id,
                'value': value,
                'reason': reason,
            },
        )

        return {'wallet_ban_id': wallet_ban.id}

    @staticmethod
    async def create_related(
            wallet: Wallet,
            value: int,
            reason: str,
    ) -> WalletBan:
        wallet_free_balance = await WalletService().get_free_value(wallet=wallet)
        if wallet_free_balance < value:
            raise NotEnoughFundsOnBalance()

        await WalletRepository().update(
            wallet,
            value=wallet.value - value,
            value_banned=wallet.value_banned + value,
        )
        wallet_ban = await WalletBanRepository().create(wallet=wallet, value=value, reason=reason)
        return wallet_ban

    @session_required(permissions=['wallets_bans'])
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        wallet_ban = await WalletBanRepository().get_by_id(id_=id_)
        await self.delete_related(wallet_ban=wallet_ban)
        await WalletBanRepository().delete(wallet_ban)
        await self.create_action(
            model=wallet_ban,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )

        return {}

    @staticmethod
    async def delete_related(wallet_ban: WalletBan) -> None:
        wallet_available_balance = await WalletService().get_available_value(wallet=wallet_ban.wallet)
        if wallet_available_balance < wallet_ban.value:
            raise WalletLimitReached(
                kwargs={
                    'wallet_max_value': settings.wallet_max_value,
                },
            )
        wallet = wallet_ban.wallet

        await WalletRepository().update(
            wallet,
            value=wallet.value + wallet_ban.value,
            value_banned=wallet.value_banned - wallet_ban.value
        )
