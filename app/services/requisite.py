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
import math
from typing import Optional

from app.db.models import Session, Requisite, RequisiteTypes, Actions, WalletBanReasons
from app.repositories.method import MethodRepository
from app.repositories.requisite import RequisiteRepository
from app.repositories.requisite_data import RequisiteDataRepository
from app.repositories.wallet import WalletRepository
from app.repositories.wallet_account import WalletAccountRepository
from app.services.base import BaseService
from app.services.wallet_ban import WalletBanService
from app.utils.decorators import session_required
from app.utils.exaptions.main import DoesNotPermission
from app.utils.exaptions.requisite import MinimumTotalValueError


class RequisiteService(BaseService):
    model = Requisite

    @session_required(permissions=['requisites'])
    async def create(
            self,
            session: Session,
            type_: int,
            wallet_id: int,
            output_requisite_data_id: int,
            input_method_id: int,
            total_currency_value: int,
            currency_value_min: int,
            currency_value_max: int,
            rate: int,
            total_value: int,
            value_min: int,
            value_max: int,
    ) -> dict:
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        if not await WalletAccountRepository().get(account=account, wallet=wallet):
            raise DoesNotPermission('You do not have sufficient rights to this wallet')
        total_currency_value_result, total_value_result, rate_result = await self.calc_value_params(
            type_=type_,
            total_currency_value=total_currency_value,
            total_value=total_value,
            rate=rate
        )
        currency = None
        output_requisite_data = None
        if output_requisite_data_id:
            output_requisite_data = await RequisiteDataRepository().get_by_id(id_=output_requisite_data_id)
            currency = output_requisite_data.method.currency
        input_method = None
        if input_method_id:
            input_method = await MethodRepository().get_by_id(id_=input_method_id)
            currency = input_method.currency

        if type_ == RequisiteTypes.OUTPUT:
            await WalletBanService().create_related(
                wallet=wallet,
                value=total_value_result,
                reason=WalletBanReasons.BY_REQUISITE,
            )

        requisite = await RequisiteRepository().create(
            type=type_,
            wallet=wallet,
            output_requisite_data=output_requisite_data,
            input_method=input_method,
            currency=currency,
            currency_value=total_currency_value_result,
            total_currency_value=total_currency_value_result,
            currency_value_min=currency_value_min,
            currency_value_max=currency_value_max,
            rate=rate_result,
            value=total_value_result,
            total_value=total_value_result,
            value_min=value_min,
            value_max=value_max,
        )
        await self.create_action(
            model=requisite,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'id': requisite.id,
                'type': type_,
                'wallet_id': wallet_id,
                'output_requisite_data_id': output_requisite_data_id,
                'input_method_id': input_method_id,
                'currency': currency.id_str,
                'total_currency_value': total_currency_value,
                'total_currency_value_result': total_currency_value_result,
                'currency_value_min': currency_value_min,
                'currency_value_max': currency_value_max,
                'rate': rate,
                'rate_result': rate_result,
                'total_value': total_value,
                'total_value_result': total_value_result,
                'value_min': value_min,
                'value_max': value_max,
            },
        )

        return {'requisite_id': requisite.id}

    @session_required(permissions=['requisites'])
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

    @session_required(permissions=['requisites'])
    async def update(
            self,
            session: Session,
            id_: int,
            total_value: int,
    ) -> dict:
        account = session.account
        requisite = await RequisiteRepository().get_by_id(id_=id_)
        if not await WalletAccountRepository().get(account=account, wallet=requisite.wallet):
            raise DoesNotPermission('You do not have sufficient rights to this wallet')
        access_change_balance = requisite.total_value - requisite.value

        if total_value < access_change_balance:
            raise MinimumTotalValueError(f'Minimum value total_value = {access_change_balance}')

        new_value = round(total_value - (requisite.total_value - requisite.value))
        new_currency_value = round(new_value * requisite.rate / 100)
        new_total_value = total_value
        new_currency_total_value = round(new_total_value * requisite.rate / 100)
        await RequisiteRepository().update(
            requisite,
            value=new_value,
            total_value=new_total_value,
            currency_value=new_currency_value,
            total_currency_value=new_currency_total_value,
        )

        await self.create_action(
            model=requisite,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'total_value': total_value,
                'new_value': new_value,
                'new_currency_value': new_currency_value,
                'new_total_value': new_total_value,
                'new_currency_total_value': new_currency_total_value,
            },
        )

        return {}

    @staticmethod
    async def calc_value_params(
            type_: RequisiteTypes,
            total_currency_value: Optional[int],
            total_value: Optional[int],
            rate: Optional[int],
    ) -> tuple[int, int, int]:
        if total_currency_value and total_value:
            if type_ == RequisiteTypes.OUTPUT:
                rate = math.ceil(total_currency_value / total_value * 100)
            else:
                rate = math.floor(total_currency_value / total_value * 100)
        elif total_currency_value and rate:
            if type_ == RequisiteTypes.OUTPUT:
                total_value = math.floor(total_currency_value / rate * 100)
            else:
                total_value = math.ceil(total_currency_value / rate * 100)
        else:
            if type_ == RequisiteTypes.OUTPUT:
                total_currency_value = math.ceil(total_value * rate / 100)
            else:
                total_currency_value = math.floor(total_value * rate / 100)
        return total_currency_value, total_value, rate
