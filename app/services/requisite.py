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
import math
from typing import Optional

from app.db.models import Session, Requisite, RequisiteTypes
from app.repositories.base import DoesNotPermission
from app.repositories.currency import CurrencyRepository
from app.repositories.requisite import RequisiteRepository, NotRequiredParams, MinimumTotalValueError
from app.repositories.requisite_data import RequisiteDataRepository
from app.repositories.wallet import WalletRepository
from app.repositories.wallet_account import WalletAccountRepository
from app.services.base import BaseService
from app.utils.custom_calc import round_ceil, round_floor
from app.utils.decorators import session_required


class RequisiteService(BaseService):
    model = Requisite

    @session_required()
    async def create(
            self,
            session: Session,
            type_: int,
            wallet_id: int,
            requisite_data_id: int,
            total_currency_value: int,
            total_currency_value_min: int,
            total_currency_value_max: int,
            rate: float,
            total_value: int,
            total_value_min: int,
            total_value_max: int,
    ) -> dict:
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        if not await WalletAccountRepository().get(account=account, wallet=wallet):
            raise DoesNotPermission('You do not have sufficient rights to this wallet')
        total_currency_value_fix, total_value_fix, rate_fix = await self.calc_value_params(
            type_=type_,
            total_currency_value=total_currency_value,
            total_value=total_value,
            rate=rate
        )

        requisite_data = await RequisiteDataRepository().get_by_id(id_=requisite_data_id)
        requisite = await RequisiteRepository().create(
            type=type_,
            wallet=wallet,
            requisite_data=requisite_data,
            currency=requisite_data.method.currency,
            currency_value=total_currency_value_fix,
            total_currency_value=total_currency_value_fix,
            total_currency_value_min=total_currency_value_min,
            total_currency_value_max=total_currency_value_max,
            rate=rate_fix,
            value=total_value_fix,
            total_value=total_value_fix,
            total_value_min=total_value_min,
            total_value_max=total_value_max,
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
                'total_currency_value': total_currency_value,
                'total_currency_value_fix': total_currency_value_fix,
                'total_currency_value_min': total_currency_value_min,
                'total_currency_value_max': total_currency_value_max,
                'rate': rate,
                'rate_fix': rate_fix,
                'total_value': total_value,
                'total_value_fix': total_value_fix,
                'total_value_min': total_value_min,
                'total_value_max': total_value_max,
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
        account = session.account
        requisite = await RequisiteRepository().get_by_id(id_=id_)
        if not await WalletAccountRepository().get(account=account, wallet=requisite.wallet):
            raise DoesNotPermission('You do not have sufficient rights to this wallet')
        access_change_balance = requisite.total_value - requisite.value

        if total_value < access_change_balance:
            raise MinimumTotalValueError(f'Minimum value total_value = {access_change_balance}')

        await RequisiteRepository().update(
            requisite,
            value=total_value - (requisite.total_value - requisite.value),
            total_value=total_value,
            currency_value=round(total_value * requisite.rate, 2)
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

    @staticmethod
    async def calc_value_params(
            type_: RequisiteTypes,
            total_currency_value: Optional[float],
            total_value: Optional[float],
            rate: Optional[float],
    ) -> tuple[float, float, float]:
        if [total_currency_value, total_value, rate].count(None) > 1:
            raise NotRequiredParams('Two of the following parameters must be filled in: '
                                    'currency_value, total_value, rate')
        if total_currency_value and total_value:
            if type_ == RequisiteTypes.INPUT:
                rate = round_ceil(total_currency_value / total_value)
            else:
                rate = round_floor(total_currency_value / total_value)
        elif total_currency_value and rate:
            if type_ == RequisiteTypes.INPUT:
                total_value = math.floor(total_currency_value / rate)
            else:
                total_value = math.ceil(total_currency_value / rate)
        else:
            if type_ == RequisiteTypes.INPUT:
                total_currency_value = math.ceil(total_value * rate)
            else:
                total_currency_value = math.floor(total_value * rate)
        return total_currency_value, total_value, rate
