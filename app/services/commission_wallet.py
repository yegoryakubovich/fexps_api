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

from app.db.models import Session, CommissionWallet, Actions
from app.repositories.commission_wallet import CommissionWalletRepository
from app.repositories.wallet import WalletRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class CommissionWalletService(BaseService):
    model = CommissionWallet

    @session_required()
    async def create(
            self,
            session: Session,
            wallet_id: int,
            percent: int,
            value: int,
    ) -> dict:
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        commission_wallet = await CommissionWalletRepository().create(
            wallet=wallet,
            percent=percent,
            value=value,
        )
        await self.create_action(
            model=commission_wallet,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'id': commission_wallet.id,
                'wallet_id': wallet_id,
                'percent': percent,
                'value': value,
            },
        )

        return {'commission_wallet_id': commission_wallet.id}

    @staticmethod
    async def get_list() -> dict:
        return {
            'commissions_wallets': [
                {
                    'id': commission_wallet.id,
                    'wallet_id': commission_wallet.wallet.id,
                    'percent': commission_wallet.percent,
                    'value': commission_wallet.value,
                }
                for commission_wallet in await CommissionWalletRepository().get_list()
            ],
        }

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        commission_wallet = await CommissionWalletRepository().get(id=id_)
        await CommissionWalletRepository().delete(commission_wallet)
        await self.create_action(
            model=commission_wallet,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )

        return {}
