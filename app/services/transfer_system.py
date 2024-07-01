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


from inflection import underscore

from app.db.base_class import Base
from app.db.models import TransferSystem, Request, TransferTypes, TransferSystemTypes, WalletBanReasons
from app.db.models.transfer_system import TransferSystemReasons
from app.repositories import WalletBanRequestRepository, TransferSystemRepository, WalletRepository
from app.services.base import BaseService
from app.services.transfer import TransferService
from app.services.wallet_ban import WalletBanService


class TransferSystemService(BaseService):
    model = TransferSystem

    @staticmethod
    async def create_transfer(
            model: Base,
            reason: str,
            wallet_id: int,
            value: int,
            description: str = None,
            ignore_bal: bool = False,
    ) -> None:
        if value == 0:
            return
        wallet_from = await WalletRepository().get_by_id(id_=wallet_id)
        wallet_to = await WalletRepository().get_system_wallet()
        transfer = await TransferService().create_transfer(
            type_=TransferTypes.IN_ORDER,
            wallet_from=wallet_from,
            wallet_to=wallet_to,
            value=value,
            ignore_bal=ignore_bal,
        )
        transfer_system_type = TransferSystemTypes.INPUT if value > 0 else TransferSystemTypes.OUTPUT
        await TransferSystemRepository().create(
            transfer=transfer,
            model=underscore(model.__class__.__name__),
            model_id=model.id,
            type=transfer_system_type,
            reason=reason,
            description=description,
        )

    async def payment_commission(
            self,
            request: Request,
            from_banned_value: bool = False,
    ) -> None:
        if not request.commission:
            return
        if from_banned_value:
            wallet_ban = await WalletBanService().create_related(
                wallet=request.wallet,
                value=-request.commission,
                reason=WalletBanReasons.BY_REQUEST,
                ignore_balance=True,
            )
            await WalletBanRequestRepository().create(wallet_ban=wallet_ban, request=request)
        await self.create_transfer(
            model=request,
            wallet_id=request.wallet_id,
            value=request.commission,
            reason=TransferSystemReasons.COMMISSION,
        )

    async def payment_difference(
            self,
            request: Request,
            value: int,
            from_banned_value: bool = False,
    ) -> None:
        if not value:
            return
        if from_banned_value:
            wallet_ban = await WalletBanService().create_related(
                wallet=request.wallet,
                value=-value,
                reason=WalletBanReasons.BY_REQUEST,
                ignore_balance=True,
            )
            await WalletBanRequestRepository().create(wallet_ban=wallet_ban, request=request)
        await self.create_transfer(
            model=request,
            wallet_id=request.wallet_id,
            value=value,
            reason=TransferSystemReasons.DIFFERENCE,
            ignore_bal=True,
        )
