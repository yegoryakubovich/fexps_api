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


from app.db.models import TransferSystem, Request, TransferTypes, TransferSystemTypes
from app.db.models.transfer_system import TransferSystemReasons
from app.repositories.transfer_system import TransferSystemRepository
from app.repositories.wallet import WalletRepository
from app.services.base import BaseService
from app.services.transfer import TransferService


class TransferSystemService(BaseService):
    model = TransferSystem

    @staticmethod
    async def create_transfer(
            reason: str,
            wallet_id: int,
            value: int,
            description: str = None,
    ) -> None:
        wallet_from = await WalletRepository().get_by_id(id_=wallet_id)
        wallet_to = await WalletRepository().get_system_wallet()
        transfer = await TransferService().transfer(
            type_=TransferTypes.IN_ORDER,
            wallet_from=wallet_from,
            wallet_to=wallet_to,
            value=value,
        )
        await TransferSystemRepository().create(
            transfer=transfer,
            type=TransferSystemTypes.INPUT,
            reason=reason,
            description=description,
        )

    async def payment_commission(
            self,
            request: Request,
    ) -> None:
        if request.commission_value:
            await self.create_transfer(
                wallet_id=request.wallet_id,
                value=request.commission_value,
                reason=TransferSystemReasons.COMMISSION,
                description=f'Request #{request.id}',
            )

    async def payment_div(
            self,
            request: Request,
    ) -> None:
        if request.div_value:
            await self.create_transfer(
                wallet_id=request.wallet_id,
                value=request.div_value,
                reason=TransferSystemReasons.DIV,
                description=f'Request #{request.id}',
            )
