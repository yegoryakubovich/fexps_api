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
from typing import Optional

from app.db.models import Session, Requisite, RequisiteTypes, Actions, WalletBanReasons, RequisiteStates, OrderStates, \
    NotificationTypes
from app.repositories import WalletAccountRepository, OrderRepository, MethodRepository, RequisiteRepository, \
    RequisiteDataRepository, WalletRepository, WalletBanRequisiteRepository
from app.services.base import BaseService
from app.services.currency import CurrencyService
from app.services.method import MethodService
from app.services.requisite_data import RequisiteDataService
from app.services.wallet import WalletService
from app.services.wallet_ban import WalletBanService
from app.utils.bot.notification import BotNotification
from app.utils.calcs.requisites.value import calcs_requisites_values_calc
from app.utils.decorators import session_required
from app.utils.exceptions import RequisiteStateWrong, RequisiteActiveOrdersExistsError
from app.utils.exceptions.requisite import RequisiteMinimumValueError
from app.utils.exceptions.wallet import WalletPermissionError
from config import settings


class RequisiteService(BaseService):
    model = Requisite

    @session_required()
    async def create(
            self,
            session: Session,
            type_: str,
            wallet_id: int,
            output_requisite_data_id: int,
            input_method_id: int,
            currency_value: int,
            rate: int,
            value: int,
            currency_value_min: int,
            currency_value_max: int,
    ) -> dict:
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        await WalletService().check_permission(
            account=account,
            wallets=[wallet],
        )
        input_method, output_method, output_requisite_data, currency = None, None, None, None
        if input_method_id:
            input_method = await MethodRepository().get_by_id(id_=input_method_id)
            currency = input_method.currency
        if output_requisite_data_id:
            output_requisite_data = await RequisiteDataRepository().get_by_id(id_=output_requisite_data_id)
            output_method = output_requisite_data.method
            currency = output_method.currency
        currency_value_result, value_result, rate_result = await calcs_requisites_values_calc(
            type_=type_,
            rate_decimal=currency.rate_decimal,
            currency_value=currency_value,
            value=value,
            rate=rate,
        )
        wallet_ban = None
        if type_ == RequisiteTypes.OUTPUT:
            wallet_ban = await WalletBanService().create_related(
                wallet=wallet,
                value=value_result,
                reason=WalletBanReasons.BY_REQUISITE,
            )
        requisite = await RequisiteRepository().create(
            type=type_,
            wallet=wallet,
            input_method=input_method,
            output_method=output_method,
            output_requisite_data=output_requisite_data,
            currency=currency,
            currency_value=currency_value_result,
            total_currency_value=currency_value_result,
            currency_value_min=currency_value_min,
            currency_value_max=currency_value_max,
            rate=rate_result,
            value=value_result,
            total_value=value_result,
        )
        if wallet_ban:
            await WalletBanRequisiteRepository().create(wallet_ban=wallet_ban, requisite=requisite)
        await BotNotification().send_notification_by_wallet(
            wallet=requisite.wallet,
            notification_type=NotificationTypes.REQUISITE,
            text_key='notification_requisite_create',
            requisite_id=requisite.id,
        )
        await self.create_action(
            model=requisite,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
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
            },
        )
        return {
            'id': requisite.id,
        }

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        requisite = await RequisiteRepository().get_by_id(id_=id_)
        await WalletService().check_permission(
            account=account,
            wallets=[requisite.wallet],
        )
        if requisite.type == RequisiteTypes.OUTPUT:
            if requisite.output_requisite_data.account.id != account.id:
                raise WalletPermissionError()
        return {
            'requisite': await self.generate_requisites_dict(requisite=requisite)
        }

    @session_required()
    async def search(
            self,
            session: Session,
            is_type_input: bool,
            is_type_output: bool,
            is_state_enable: bool,
            is_state_stop: bool,
            is_state_disable: bool,
            page: int,
    ) -> dict:
        account = session.account
        wallets = [
            wallet_account.wallet
            for wallet_account in await WalletAccountRepository().get_list(account=account)
        ]
        requisites, results = await RequisiteRepository().search(
            wallets=wallets,
            is_type_input=is_type_input,
            is_type_output=is_type_output,
            is_state_enable=is_state_enable,
            is_state_stop=is_state_stop,
            is_state_disable=is_state_disable,
            page=page,
        )
        requisites = [
            await self.generate_requisites_dict(requisite=requisite)
            for requisite in requisites
        ]
        return {
            'requisites': requisites,
            'results': results,
            'pages': ceil(results / settings.items_per_page),
            'page': page,
            'items_per_page': settings.items_per_page,
        }

    @session_required()
    async def update_stop(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        need_state = RequisiteStates.ENABLE
        next_state = RequisiteStates.STOP
        requisite = await RequisiteRepository().get_by_id(id_=id_)
        await WalletService().check_permission(
            account=account,
            wallets=[requisite.wallet],
        )
        if requisite.state != need_state:
            raise RequisiteStateWrong(
                kwargs={
                    'id_value': requisite.id,
                    'state': requisite.state,
                    'need_state': need_state,
                },
            )
        await RequisiteRepository().update(requisite, state=next_state)
        await BotNotification().send_notification_by_wallet(
            wallet=requisite.wallet,
            notification_type=NotificationTypes.REQUISITE,
            text_key=f'notification_requisite_update_state_{next_state}',
            requisite_id=requisite.id,
        )
        await self.create_action(
            model=requisite,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'state': next_state,
            },
        )
        return {}

    @session_required()
    async def update_enable(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        need_state = RequisiteStates.STOP
        next_state = RequisiteStates.ENABLE
        requisite = await RequisiteRepository().get_by_id(id_=id_)
        await WalletService().check_permission(
            account=account,
            wallets=[requisite.wallet],
        )
        if requisite.state != need_state:
            raise RequisiteStateWrong(
                kwargs={
                    'id_value': requisite.id,
                    'state': requisite.state,
                    'need_state': need_state,
                },
            )
        await RequisiteRepository().update(requisite, state=next_state)
        await BotNotification().send_notification_by_wallet(
            wallet=requisite.wallet,
            notification_type=NotificationTypes.REQUISITE,
            text_key=f'notification_requisite_update_state_{next_state}',
            requisite_id=requisite.id,
        )
        await self.create_action(
            model=requisite,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'state': next_state,
            },
        )
        return {}

    @session_required()
    async def update_disable(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        need_state = RequisiteStates.STOP
        next_state = RequisiteStates.DISABLE
        requisite = await RequisiteRepository().get_by_id(id_=id_)
        await WalletService().check_permission(
            account=account,
            wallets=[requisite.wallet],
        )
        if requisite.state != need_state:
            raise RequisiteStateWrong(
                kwargs={
                    'id_value': requisite.id,
                    'state': requisite.state,
                    'need_state': need_state,
                },
            )
        for order_state in [OrderStates.WAITING, OrderStates.PAYMENT, OrderStates.CONFIRMATION]:
            if await OrderRepository().get_list(requisite=requisite, state=order_state):
                raise RequisiteActiveOrdersExistsError(
                    kwargs={
                        'id_value': requisite.id,
                        'action': f'Change state to {next_state}',
                    },
                )
        await self.update_value_related(
            requisite=requisite,
            value=-requisite.value,
        )
        await RequisiteRepository().update(requisite, state=next_state)
        await BotNotification().send_notification_by_wallet(
            wallet=requisite.wallet,
            notification_type=NotificationTypes.REQUISITE,
            text_key=f'notification_requisite_update_state_{next_state}',
            requisite_id=requisite.id,
        )
        await self.create_action(
            model=requisite,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'state': next_state,
            },
        )
        return {}

    @session_required()
    async def update_value(
            self,
            session: Session,
            id_: int,
            total_currency_value: int,
    ) -> dict:
        account = session.account
        requisite = await RequisiteRepository().get_by_id(id_=id_)
        await WalletService().check_permission(
            account=account,
            wallets=[requisite.wallet],
        )
        total_value = round(total_currency_value / requisite.rate * 10 ** requisite.currency.rate_decimal)
        access_change_balance = requisite.total_value - requisite.value
        if total_value < access_change_balance:
            raise RequisiteMinimumValueError(
                kwargs={
                    'access_change_balance': access_change_balance,
                },
            )
        value = total_value - requisite.total_value
        await self.update_value_related(
            requisite=requisite,
            value=value,
        )
        await self.create_action(
            model=requisite,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'total_value': total_value,
            },
        )
        return {}

    @staticmethod
    async def update_value_related(requisite: Requisite, value: int):
        wallet = requisite.wallet
        currency = requisite.currency
        new_total_value = requisite.total_value + value
        new_value = requisite.value + value
        new_total_currency_value = round(new_total_value * requisite.rate / 10 ** currency.rate_decimal)
        new_currency_value = round(new_value * requisite.rate / 10 ** currency.rate_decimal)
        if requisite.type == RequisiteTypes.OUTPUT:
            wallet_ban = await WalletBanService().create_related(
                wallet=wallet,
                value=value,
                reason=WalletBanReasons.BY_REQUISITE,
            )
            await WalletBanRequisiteRepository().create(wallet_ban=wallet_ban, requisite=requisite)
        await RequisiteRepository().update(
            requisite,
            total_value=new_total_value,
            value=new_value,
            total_currency_value=new_total_currency_value,
            currency_value=new_currency_value,
        )

    @session_required(permissions=['requisites'], can_root=True)
    async def empty_by_task(self, session: Session):
        for requisite in await RequisiteRepository().get_list_empty(requisite_state=RequisiteStates.ENABLE):
            active_order = False
            for state in [OrderStates.WAITING, OrderStates.PAYMENT, OrderStates.CONFIRMATION]:
                if OrderRepository().get_list(requisite=requisite, state=state):
                    active_order = True
                    break
            if active_order:
                continue
            await RequisiteRepository().update(requisite, state=RequisiteStates.STOP)
            await BotNotification().send_notification_by_wallet(
                wallet=requisite.wallet,
                notification_type=NotificationTypes.REQUISITE,
                text_key='notification_requisite_auto_update_state_stop',
                requisite_id=requisite.id,
            )
        return {}

    @staticmethod
    async def generate_requisites_dict(requisite: Requisite) -> Optional[dict]:
        if not requisite:
            return
        input_method = None
        if requisite.input_method:
            input_method = await MethodService().generate_method_dict(method=requisite.input_method)
        output_requisite_data, output_method = None, None
        if requisite.output_requisite_data:
            output_requisite_data = await RequisiteDataService().generate_requisite_data_dict(
                requisite_data=requisite.output_requisite_data,
            )
            output_method = await MethodService().generate_method_dict(
                method=requisite.output_requisite_data.method,
            )
        return {
            'id': requisite.id,
            'type': requisite.type,
            'state': requisite.state,
            'wallet': await WalletService().generate_wallet_dict(wallet=requisite.wallet),
            'input_method': input_method,
            'output_method': output_method,
            'output_requisite_data': output_requisite_data,
            'currency': await CurrencyService().generate_currency_dict(currency=requisite.currency),
            'currency_value': requisite.currency_value,
            'total_currency_value': requisite.total_currency_value,
            'currency_value_min': requisite.currency_value_min,
            'currency_value_max': requisite.currency_value_max,
            'rate': requisite.rate,
            'value': requisite.value,
            'total_value': requisite.total_value,
        }
