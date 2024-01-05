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
from typing import Optional

from app.db.models import Session, Requisite
from app.repositories.base import DoesNotPermission
from app.repositories.currency import CurrencyRepository
from app.repositories.requisite import RequisiteRepository, NotRequiredParams, MinimumTotalValueError
from app.repositories.requisite_data import RequisiteDataRepository
from app.repositories.wallet import WalletRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class RequisiteService(BaseService):
    model = Requisite

    @staticmethod
    async def calc_value_params(
            currency_value: Optional[float],
            total_value: Optional[float],
            rate: Optional[float],
    ) -> tuple[float, float, float]:
        if [currency_value, total_value, rate].count(None) > 1:
            raise NotRequiredParams(
                'Two of the following parameters must be filled in: currency_value, total_value, rate'
            )
        if currency_value and total_value:
            rate = round(currency_value / total_value, 2)
        elif currency_value and rate:
            total_value = round(currency_value * rate, 2)
        else:
            currency_value = round(total_value * rate, 2)
        return currency_value, total_value, rate

    @session_required()
    async def create(
            self,
            session: Session,
            type_: int,
            wallet_id: int,
            requisite_data_id: int,
            currency_id_str: str,
            currency_value: float,
            rate: float,
            total_value: float,
            value_min: float,
            value_max: float,
    ) -> dict:
        currency_value_fix, total_value_fix, rate_fix = await self.calc_value_params(
            currency_value=currency_value,
            total_value=total_value,
            rate=rate
        )
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        requisite_data = await RequisiteDataRepository().get_by_id(id_=requisite_data_id)
        currency = await CurrencyRepository().get_by_id_str(id_str=currency_id_str)
        requisite = await RequisiteRepository().create(
            type=type_,
            wallet=wallet,
            requisite_data=requisite_data,
            currency=currency,
            currency_value=currency_value_fix,
            rate=rate_fix,
            value=total_value_fix,
            total_value=total_value_fix,
            value_min=value_min,
            value_max=value_max,
        )
        await self.create_action(
            model=requisite,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id': requisite.id,
                'type': type_,
                'wallet_id': wallet_id,
                'requisite_data_id': requisite_data_id,
                'currency': currency_id_str,
                'currency_value': currency_value,
                'total_value': total_value,
                'value_min': value_min,
                'value_max': value_max,
            },
        )
        return {'requisite_id': requisite.id}

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        requisite = await RequisiteRepository().get_by_id(id_=id_)
        if requisite.requisite_data.account.id != account.id and requisite.wallet.account.id != account.id:
            raise DoesNotPermission('You do not have sufficient rights to this wallet or requisite_data')
        return {
            'requisite': {
                'id': requisite.id,
                'type': requisite.type,
                'wallet_id': requisite.wallet.id,
                'requisite_data_id': requisite.requisite_data.id,
                'currency': requisite.currency.id_str,
                'currency_value': requisite.currency_value,
                'rate': requisite.rate,
                'value': requisite.value,
                'total_value': requisite.total_value,
                'value_min': requisite.value_min,
                'value_max': requisite.value_max,
            }
        }

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            total_value: float,
    ) -> dict:
        requisite = await RequisiteRepository().get_by_id(id_=id_)
        access_change_balance = requisite.total_value - requisite.value

        if total_value < access_change_balance:
            raise MinimumTotalValueError(f'Minimum value total_value = {access_change_balance}')

        await RequisiteRepository().update(
            requisite,
            value=1,
        )

        await self.create_action(
            model=requisite,
            action='update',
            parameters={
                'updater': f'session_{session.id}',
                'total_value': total_value,
            },
        )

        return {}
