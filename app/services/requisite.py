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
from math import ceil

from app.db.models import Session, Requisite, RequisiteTypes, Actions, WalletBanReasons
from app.repositories import WalletAccountRepository
from app.repositories.method import MethodRepository
from app.repositories.requisite import RequisiteRepository
from app.repositories.requisite_data import RequisiteDataRepository
from app.repositories.wallet import WalletRepository
from app.services.base import BaseService
from app.services.wallet_ban import WalletBanService
from app.utils.calculations.requisite import all_value_calc
from app.utils.decorators import session_required
from app.utils.exceptions.requisite import RequisiteMinimumValueError
from app.utils.exceptions.wallet import WalletPermissionError
from app.utils.service_addons.wallet import wallet_check_permission
from config import settings


class RequisiteService(BaseService):
    model = Requisite

    @session_required()
    async def create(
            self,
            session: Session,
            type_: int,
            wallet_id: int,
            output_requisite_data_id: int,
            input_method_id: int,
            currency_value: int,
            currency_value_min: int,
            currency_value_max: int,
            rate: int,
            value: int,
            value_min: int,
            value_max: int,
    ) -> dict:
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        await wallet_check_permission(account=account, wallets=[wallet])
        input_method, output_requisite_data, currency = None, None, None
        if input_method_id:
            input_method = await MethodRepository().get_by_id(id_=input_method_id)
            currency = input_method.currency
        if output_requisite_data_id:
            output_requisite_data = await RequisiteDataRepository().get_by_id(id_=output_requisite_data_id)
            currency = output_requisite_data.method.currency
        currency_value_result, value_result, rate_result = await all_value_calc(
            type_=type_, rate_decimal=currency.rate_decimal, currency_value=currency_value, value=value, rate=rate,
        )
        if type_ == RequisiteTypes.OUTPUT:
            await WalletBanService().create_related(
                wallet=wallet, value=value_result, reason=WalletBanReasons.BY_REQUISITE,
            )
        requisite = await RequisiteRepository().create(
            type=type_,
            wallet=wallet,
            output_requisite_data=output_requisite_data,
            input_method=input_method,
            currency=currency,
            currency_value=currency_value_result,
            total_currency_value=currency_value_result,
            currency_value_min=currency_value_min,
            currency_value_max=currency_value_max,
            rate=rate_result,
            value=value_result,
            total_value=value_result,
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
                'currency_value': currency_value,
                'currency_value_result': currency_value_result,
                'currency_value_min': currency_value_min,
                'currency_value_max': currency_value_max,
                'rate': rate,
                'rate_result': rate_result,
                'value': value,
                'value_result': value_result,
                'value_min': value_min,
                'value_max': value_max,
            },
        )

        return {'id': requisite.id}

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        requisite = await RequisiteRepository().get_by_id(id_=id_)
        await wallet_check_permission(account=account, wallets=[requisite.wallet])
        if requisite.type == RequisiteTypes.OUTPUT:
            if requisite.output_requisite_data.account.id != account.id:
                raise WalletPermissionError()
        return {
            'requisite': self._generate_requisites_dict(requisite=requisite)
        }

    @session_required()
    async def search(
            self,
            session: Session,
            is_input: bool,
            is_output: bool,
            page: int,
    ) -> dict:
        account = session.account
        wallets = [
            wallet_account.wallet
            for wallet_account in await WalletAccountRepository().get_list(account=account)
        ]
        requisites, results = await RequisiteRepository().search(
            wallets=wallets,
            is_input=is_input,
            is_output=is_output,
            page=page,
        )
        requisites = [
            self._generate_requisites_dict(requisite=requisite)
            for requisite in requisites
        ]
        return {
            'requisites': requisites,
            'results': results,
            'pages': ceil(results / settings.items_per_page),
            'page': page,
            'items_per_page': settings.items_per_page,
        }

    @session_required()  # FIXME (CHECKME)
    async def update(
            self,
            session: Session,
            id_: int,
            total_value: int,
    ) -> dict:
        account = session.account
        requisite = await RequisiteRepository().get_by_id(id_=id_)
        await wallet_check_permission(account=account, wallets=[requisite.wallet])
        access_change_balance = requisite.total_value - requisite.value
        if total_value < access_change_balance:
            raise RequisiteMinimumValueError(kwargs={'access_change_balance': access_change_balance})

        new_value = round(total_value - (requisite.total_value - requisite.value))
        new_currency_value = round(new_value * requisite.rate / 10 ** settings.rate_decimal)
        new_total_value = total_value
        new_currency_total_value = round(new_total_value * requisite.rate / 10 ** settings.rate_decimal)
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
    def _generate_requisites_dict(requisite: Requisite):
        return {
            'id': requisite.id,
            'type': requisite.type,
            'wallet_id': requisite.wallet.id,
            'input_method_id': requisite.input_method_id,
            'output_method_id': requisite.output_requisite_data.method_id if requisite.output_requisite_data else None,
            'output_requisite_data': requisite.output_requisite_data_id,
            'currency': requisite.currency.id_str,
            'currency_value': requisite.currency_value,
            'total_currency_value': requisite.total_currency_value,
            'currency_value_min': requisite.currency_value_min,
            'currency_value_max': requisite.currency_value_max,
            'rate': requisite.rate,
            'value': requisite.value,
            'total_value': requisite.total_value,
            'value_min': requisite.value_min,
            'value_max': requisite.value_max,
        }
