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


import datetime
from math import ceil

from app.db.models import Session, Request, Actions, RequestStates, RequestTypes, RequestFirstLine, OrderStates, \
    NotificationTypes
from app.repositories import WalletAccountRepository, OrderRepository
from app.repositories.method import MethodRepository
from app.repositories.request import RequestRepository
from app.repositories.requisite_data import RequisiteDataRepository
from app.repositories.wallet import WalletRepository
from app.services.action import ActionService
from app.services.base import BaseService
from app.services.currency import CurrencyService
from app.services.method import MethodService
from app.services.requisite_data import RequisiteDataService
from app.services.wallet import WalletService
from app.utils.bot.notification import BotNotification
from app.utils.calculations.request.full.all import get_auto_rate, calc_request_full_all
from app.utils.calculations.request.full.input import calc_request_full_input
from app.utils.calculations.request.full.output import calc_request_full_output
from app.utils.decorators import session_required
from app.utils.exceptions import MethodNotSupportedRoot
from app.utils.exceptions.request import RequestStateWrong, RequestStateNotPermission
from app.utils.exceptions.wallet import NotEnoughFundsOnBalance
from app.utils.service_addons.order import order_cancel_related
from app.utils.service_addons.wallet import wallet_check_permission
from config import settings


class RequestService(BaseService):
    model = Request

    @session_required()
    async def create(
            self,
            session: Session,
            wallet_id: int,
            type_: str,
            input_method_id: int,
            input_currency_value: int,
            input_value: int,
            output_currency_value: int,
            output_value: int,
            output_requisite_data_id: int,
    ) -> dict:
        first_line, first_line_value = None, None
        input_method, output_requisite_data, output_method = None, None, None
        if input_currency_value:
            first_line = RequestFirstLine.INPUT_CURRENCY_VALUE
            first_line_value = input_currency_value
        elif input_value:
            first_line = RequestFirstLine.INPUT_VALUE
            first_line_value = input_value
        elif output_currency_value:
            first_line = RequestFirstLine.OUTPUT_CURRENCY_VALUE
            first_line_value = output_currency_value
        elif output_value:
            first_line = RequestFirstLine.OUTPUT_VALUE
            first_line_value = output_value
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        rate_decimal = []
        if input_method_id:
            input_method = await MethodRepository().get_by_id(id_=input_method_id)
            rate_decimal.append(input_method.currency.rate_decimal)
        if output_requisite_data_id:
            output_requisite_data = await RequisiteDataRepository().get_by_id(id_=output_requisite_data_id)
            output_method = output_requisite_data.method
            rate_decimal.append(output_method.currency.rate_decimal)
        if type_ == RequestTypes.OUTPUT and output_value:
            balance = wallet.value - wallet.value_can_minus
            if output_value > balance:
                raise NotEnoughFundsOnBalance()
        request = await RequestRepository().create(
            wallet=wallet,
            state=RequestStates.LOADING,
            type=type_,
            rate_decimal=max(rate_decimal),
            first_line=first_line,
            first_line_value=first_line_value,
            input_method=input_method,
            output_requisite_data=output_requisite_data,
            output_method=output_method,
        )
        await BotNotification().send_notification_by_wallet(
            wallet=request.wallet,
            notification_type=NotificationTypes.REQUEST_CHANGE,
            text_key='notification_request_create',
            request_id=request.id,
        )
        await self.create_action(
            model=request,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'wallet_id': wallet_id,
                'first_line': first_line,
                'first_line_value': input_currency_value,
                'input_method_id': input_method_id,
                'output_requisite_data_id': output_requisite_data_id,
            },
        )
        return {
            'id': request.id,
        }

    @session_required()
    async def calc(
            self,
            session: Session,
            wallet_id: int,
            type_: str,
            input_method_id: int,
            input_currency_value: int,
            input_value: int,
            output_currency_value: int,
            output_value: int,
            output_requisite_data_id: int,
    ) -> dict:
        first_line, first_line_value = None, None
        input_method, output_requisite_data, output_method = None, None, None
        if input_currency_value:
            first_line = RequestFirstLine.INPUT_CURRENCY_VALUE
            first_line_value = input_currency_value
        elif input_value:
            first_line = RequestFirstLine.INPUT_VALUE
            first_line_value = input_value
        elif output_currency_value:
            first_line = RequestFirstLine.OUTPUT_CURRENCY_VALUE
            first_line_value = output_currency_value
        elif output_value:
            first_line = RequestFirstLine.OUTPUT_VALUE
            first_line_value = output_value
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        rate_decimal = []
        if input_method_id:
            input_method = await MethodRepository().get_by_id(id_=input_method_id)
            rate_decimal.append(input_method.currency.rate_decimal)
        if output_requisite_data_id:
            output_requisite_data = await RequisiteDataRepository().get_by_id(id_=output_requisite_data_id)
            output_method = output_requisite_data.method
            rate_decimal.append(output_method.currency.rate_decimal)
        if type_ == RequestTypes.OUTPUT and output_value:
            balance = wallet.value - wallet.value_can_minus
            if output_value > balance:
                raise NotEnoughFundsOnBalance()
        rate_decimal = max(rate_decimal)
        if type_ == RequestTypes.ALL:  # ALL
            result_all_type = await calc_request_full_all(
                wallet=wallet,
                input_method=input_method,
                output_method=output_method,
                first_line_value=first_line_value,
                first_line=first_line,
                type_=type_,
                rate_decimal=rate_decimal,
            )
            if not result_all_type:
                raise MethodNotSupportedRoot()
            rate = get_auto_rate(
                first_line=first_line,
                type_=type_,
                rate_decimal=rate_decimal,
                currency_value=result_all_type.input_type.currency_value,
                value=result_all_type.output_type.currency_value,
            )
            return {
                'input_currency_value_raw': result_all_type.input_type.currency_value,
                'input_value_raw': result_all_type.input_type.value,
                'input_rate_raw': result_all_type.input_rate,
                'output_currency_value_raw': result_all_type.output_type.currency_value,
                'output_value_raw': result_all_type.output_type.value,
                'output_rate_raw': result_all_type.output_rate,
                'commission_value': result_all_type.commission_value,
                'rate': rate,
                'rate_decimal': rate_decimal,
                'div_value': 0,
            }
        elif type_ == RequestTypes.INPUT:  # INPUT
            currency_value, value = None, None
            if first_line == RequestFirstLine.INPUT_CURRENCY_VALUE:
                currency_value = first_line_value
            elif first_line == RequestFirstLine.INPUT_VALUE:
                value = first_line_value
            result_type = await calc_request_full_input(
                first_line=first_line,
                input_method=input_method,
                rate_decimal=rate_decimal,
                wallet_id=wallet.id,
                currency_value=currency_value,
                value=value,
            )
            if not result_type:
                raise MethodNotSupportedRoot()
            input_rate = get_auto_rate(
                first_line=first_line,
                type_=type_,
                rate_decimal=rate_decimal,
                currency_value=result_type.currency_value,
                value=result_type.value,
            )
            return {
                'input_currency_value_raw': result_type.currency_value,
                'input_value_raw': result_type.value,
                'input_rate_raw': input_rate,
                'commission_value': result_type.commission_value,
                'rate': input_rate,
                'rate_decimal': rate_decimal,
            }
        elif type_ == RequestTypes.OUTPUT:  # OUTPUT
            currency_value, value = None, None
            if first_line == RequestFirstLine.OUTPUT_CURRENCY_VALUE:
                currency_value = first_line_value
            elif first_line == RequestFirstLine.OUTPUT_VALUE:
                value = first_line_value
            result_type = await calc_request_full_output(
                output_method=output_method,
                rate_decimal=rate_decimal,
                currency_value=currency_value,
                value=value
            )
            if not result_type:
                raise MethodNotSupportedRoot()
            output_rate = get_auto_rate(
                first_line=first_line,
                type_=type_,
                rate_decimal=rate_decimal,
                currency_value=result_type.currency_value,
                value=result_type.value,
            )
            return {
                'output_currency_value_raw': result_type.currency_value,
                'output_value_raw': result_type.value,
                'output_rate_raw': output_rate,
                'commission_value': result_type.commission_value,
                'rate': output_rate,
                'rate_decimal': rate_decimal,
            }
        return {}

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        request = await RequestRepository().get_by_id(id_=id_)
        await wallet_check_permission(
            account=account,
            wallets=[request.wallet],
            exception=RequestStateNotPermission(
                kwargs={
                    'id_value': request.id,
                    'action': f'Get by id',
                },
            )
        )
        return {
            'request': await self.generate_request_dict(request=request)
        }

    @session_required()
    async def search(
            self,
            session: Session,
            is_completed: bool,
            is_canceled: bool,
            page: int,
    ) -> dict:
        account = session.account
        wallets = [
            wallet_account.wallet
            for wallet_account in await WalletAccountRepository().get_list(account=account)
        ]
        _requests, results = await RequestRepository().search(
            wallets=wallets,
            is_completed=is_completed,
            is_canceled=is_canceled,
            page=page,
        )
        requests = []
        for _request in _requests:
            requests.append(await self.generate_request_dict(request=_request))
        return {
            'requests': requests,
            'results': results,
            'pages': ceil(results / settings.items_per_page),
            'page': page,
            'items_per_page': settings.items_per_page,
        }

    @session_required()
    async def update_confirmation(
            self,
            session: Session,
            id_: int,
            answer: bool,
    ):
        account = session.account
        request = await RequestRepository().get_by_id(id_=id_)
        if answer:
            next_state = RequestStates.INPUT_RESERVATION
            if request.type == RequestTypes.OUTPUT:
                next_state = RequestStates.OUTPUT_RESERVATION
        else:
            await self.cancel_related(request=request)
            next_state = RequestStates.CANCELED
        await wallet_check_permission(
            account=account,
            wallets=[request.wallet],
            exception=RequestStateNotPermission(
                kwargs={
                    'id_value': request.id,
                    'action': f'Update state to {next_state}',
                }
            )
        )
        if request.state != RequestStates.WAITING:
            raise RequestStateWrong(
                kwargs={
                    'id_value': request.id,
                    'state': request.state,
                    'need_state': RequestStates.WAITING,
                },
            )
        await RequestRepository().update(request, state=next_state)
        await BotNotification().send_notification_by_wallet(
            wallet=request.wallet,
            notification_type=NotificationTypes.REQUEST_CHANGE,
            text_key=f'notification_request_update_state',
            request_id=request.id,
            state=next_state,
        )
        await self.create_action(
            model=request,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'answer': answer,
                'state': next_state,
            },
        )
        return {}

    @session_required()
    async def update_name(
            self,
            session: Session,
            id_: int,
            name: str,
    ):
        account = session.account
        request = await RequestRepository().get_by_id(id_=id_)
        await wallet_check_permission(
            account=account,
            wallets=[request.wallet],
            exception=RequestStateNotPermission(
                kwargs={
                    'id_value': request.id,
                    'action': f'Update name',
                },
            ),
        )
        await RequestRepository().update(request, name=name)
        await BotNotification().send_notification_by_wallet(
            wallet=request.wallet,
            notification_type=NotificationTypes.REQUEST_CHANGE,
            text_key=f'notification_request_update_name',
            request_id=request.id,
            name=name,
        )
        await self.create_action(
            model=request,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'name': name,
            },
        )
        return {}

    @staticmethod
    async def cancel_related(request: Request) -> None:
        for order in await OrderRepository().get_list(request=request):
            if order.state == OrderStates.CANCELED:
                continue
            await order_cancel_related(order=order)
            await OrderRepository().update(order, state=OrderStates.CANCELED)
            bot_notification = BotNotification()
            await bot_notification.send_notification_by_wallet(
                wallet=order.request.wallet,
                notification_type=NotificationTypes.ORDER_CHANGE,
                text_key='notification_order_update_state',
                order_id=order.id,
                state=OrderStates.CANCELED,
            )
            await bot_notification.send_notification_by_wallet(
                wallet=order.requisite.wallet,
                notification_type=NotificationTypes.ORDER_CHANGE,
                text_key='notification_order_update_state',
                order_id=order.id,
                state=OrderStates.CANCELED,
            )

    @staticmethod
    async def generate_request_dict(request: Request) -> dict:
        action = await ActionService().get_action(model=request, action=Actions.CREATE)
        date = action.datetime.strftime(settings.datetime_format)
        update_action = await ActionService().get_action(model=request, action=Actions.UPDATE)
        waiting_delta = None
        if request.state == RequestStates.WAITING and update_action:
            time_now = datetime.datetime.now(tz=datetime.timezone.utc)
            time_update = update_action.datetime.replace(tzinfo=datetime.timezone.utc)
            time_delta = datetime.timedelta(minutes=settings.request_waiting_check)
            waiting_delta = (time_delta - (time_now - time_update)).seconds

        input_method, input_currency = None, None
        if request.input_method:
            input_method = await MethodService().generate_method_dict(method=request.input_method)
            input_currency = await CurrencyService().generate_currency_dict(currency=request.input_method.currency)
        output_method, output_currency = None, None
        if request.output_method:
            output_method = await MethodService().generate_method_dict(method=request.output_method)
            output_currency = await CurrencyService().generate_currency_dict(currency=request.output_method.currency)
        output_requisite_data = None
        if request.output_requisite_data:
            output_requisite_data = await RequisiteDataService().generate_requisite_data_dict(
                requisite_data=request.output_requisite_data,
            )
        return {
            'id': request.id,
            'name': request.name,
            'wallet': await WalletService().generate_wallet_dict(wallet=request.wallet),
            'type': request.type,
            'state': request.state,
            'rate_decimal': request.rate_decimal,
            'rate_confirmed': request.rate_confirmed,
            'difference_confirmed': request.difference_confirmed,
            'first_line': request.first_line,
            'first_line_value': request.first_line_value,
            'input_currency': input_currency,
            'input_currency_value_raw': request.input_currency_value_raw,
            'input_currency_value': request.input_currency_value,
            'input_value_raw': request.input_value_raw,
            'input_value': request.input_value,
            'input_rate_raw': request.input_rate_raw,
            'input_rate': request.input_rate,
            'commission_value': request.commission_value,
            'rate': request.rate,
            'output_currency': output_currency,
            'output_currency_value_raw': request.output_currency_value_raw,
            'output_currency_value': request.output_currency_value,
            'output_value_raw': request.output_value_raw,
            'output_value': request.output_value,
            'output_rate_raw': request.output_rate_raw,
            'output_rate': request.output_rate,
            'input_method': input_method,
            'output_requisite_data': output_requisite_data,
            'output_method': output_method,
            'date': date,
            'waiting_delta': waiting_delta,
        }
