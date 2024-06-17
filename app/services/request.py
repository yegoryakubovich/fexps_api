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
import logging
from math import ceil
from typing import Optional

from app.db.models import Session, Request, Actions, RequestStates, RequestTypes, OrderStates, \
    NotificationTypes
from app.repositories import WalletAccountRepository, OrderRepository, RatePairRepository, CurrencyRepository, \
    MethodRepository, RequisiteDataRepository
from app.repositories.request import RequestRepository
from app.repositories.wallet import WalletRepository
from app.services.action import ActionService
from app.services.base import BaseService
from app.services.method import MethodService
from app.services.requisite_data import RequisiteDataService
from app.services.wallet import WalletService
from app.utils.bot.notification import BotNotification
from app.utils.calculations.request.rate.all import calculate_request_rate_all
from app.utils.calculations.request.rate.input import calculate_request_rate_input
from app.utils.calculations.request.rate.output import calculate_request_rate_output
from app.utils.decorators import session_required
from app.utils.exceptions import RequestRatePairNotFound
from app.utils.exceptions.request import RequestStateWrong, RequestStateNotPermission
from app.utils.service_addons.order import order_cancel_related
from app.utils.service_addons.wallet import wallet_check_permission
from config import settings


class RequestService(BaseService):
    model = Request

    @session_required()
    async def create(
            self,
            session: Session,
            name: Optional[str],
            wallet_id: int,
            type_: str,
            input_method_id: Optional[int],
            output_requisite_data_id: Optional[int],
            input_value: Optional[int],
            output_value: Optional[int],
    ) -> dict:
        logging.critical(dict(
            session=session,
            name=name,
            wallet_id=wallet_id,
            type_=type_,
            input_method_id=input_method_id,
            output_requisite_data_id=output_requisite_data_id,
            input_value=input_value,
            output_value=output_value,
        ))
        start_value, end_value = input_value, output_value
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        rates_decimals = []
        input_method, output_requisite_data = None, None
        if input_method_id:
            input_method = await MethodRepository().get_by_id(id_=input_method_id)
            rates_decimals.append(input_method.currency.rate_decimal)
        if output_requisite_data_id:
            output_requisite_data = await RequisiteDataRepository().get_by_id(id_=output_requisite_data_id)
            rates_decimals.append(output_requisite_data.method.currency.rate_decimal)
        rate_decimal = max(rates_decimals)
        if type_ == RequestTypes.INPUT:
            input_currency_value, input_value = start_value, end_value
            calculate = await calculate_request_rate_input(
                input_method=input_method,
                commission_pack=wallet.commission_pack,
                input_currency_value=input_currency_value,
                input_value=input_value,
            )
        elif type_ == RequestTypes.OUTPUT:
            output_value, output_currency_value = start_value, end_value
            calculate = await calculate_request_rate_output(
                output_method=output_requisite_data.method,
                commission_pack=wallet.commission_pack,
                output_value=output_value,
                output_currency_value=output_currency_value,
            )
        else:
            input_currency_value, output_currency_value = start_value, end_value
            calculate = await calculate_request_rate_all(
                input_method=input_method,
                output_method=output_requisite_data.method,
                commission_pack=wallet.commission_pack,
                input_currency_value=input_currency_value,
                output_currency_value=output_currency_value,
            )
            if not calculate:
                raise RequestRatePairNotFound(
                    kwargs={
                        'input_currency': input_method.currency.id_str,
                        'output_currency': output_requisite_data.method.currency.id_str,
                    }
                )
        request = await RequestRepository().create(
            name=name,
            wallet=wallet,
            state=RequestStates.CONFIRMATION,
            type=type_,
            rate_decimal=rate_decimal,
            rate_fixed=True,
            difference=0,
            difference_rate=0,
            commission=calculate.commission,
            rate=calculate.rate,
            input_method=input_method,
            output_requisite_data=output_requisite_data,
            output_method=output_requisite_data.method,
            input_currency_value=calculate.input_currency_value,
            input_value=calculate.input_value,
            input_rate=calculate.input_rate,
            output_currency_value=calculate.output_currency_value,
            output_value=calculate.output_value,
            output_rate=calculate.output_rate,
        )
        await BotNotification().send_notification_by_wallet(
            wallet=request.wallet,
            notification_type=NotificationTypes.REQUEST,
            text_key='notification_request_create',
            request_id=request.id,
        )
        await self.create_action(
            model=request,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'wallet_id': wallet_id,
                'type_': type_,
                'name': name,
                'input_method_id': input_method_id,
                'output_requisite_data_id': output_requisite_data_id,
                'start_value': start_value,
                'end_value': end_value,
                'rate_decimal': rate_decimal,
                'rate_fixed': True,
                'difference': 0,
                'difference_rate': 0,
                'commission': calculate.commission,
                'rate': calculate.rate,
                'input_currency_value': calculate.input_currency_value,
                'input_value': calculate.input_value,
                'input_rate': calculate.input_rate,
                'output_currency_value': calculate.output_currency_value,
                'output_value': calculate.output_value,
                'output_rate': calculate.output_rate,
            },
        )
        return {
            'id': request.id,
        }

    @session_required()
    async def calculate(
            self,
            session: Session,
            type_: str,
            input_currency_id_str: str,
            output_currency_id_str: str,
    ) -> dict:
        account = session.account
        input_currency, output_currency = None, None
        if input_currency_id_str:
            input_currency = await CurrencyRepository().get_by_id_str(id_str=input_currency_id_str)
        if output_currency_id_str:
            output_currency = await CurrencyRepository().get_by_id_str(id_str=output_currency_id_str)
        if type_ == RequestTypes.ALL:  # ALL
            pass
        elif type_ == RequestTypes.INPUT:  # INPUT
            output_currency = await CurrencyRepository().get_by_id_str(id_str='usdt')
        elif type_ == RequestTypes.OUTPUT:  # OUTPUT
            input_currency = await CurrencyRepository().get_by_id_str(id_str='usdt')
        rate_pair = await RatePairRepository().get(
            currency_input=output_currency,
            currency_output=input_currency,
        )
        if not rate_pair:
            raise RequestRatePairNotFound(
                kwargs={
                    'input_currency': input_currency.id_str,
                    'output_currency': output_currency.id_str,
                }
            )
        return {
            'input_currency': rate_pair.currency_input.id_str,
            'output_currency': rate_pair.currency_output.id_str,
            'rate': rate_pair.value,
            'rate_decimal': rate_pair.rate_decimal,
        }

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
        if request.state != RequestStates.CONFIRMATION:
            raise RequestStateWrong(
                kwargs={
                    'id_value': request.id,
                    'state': request.state,
                    'need_state': RequestStates.CONFIRMATION,
                },
            )
        await RequestRepository().update(request, state=next_state)
        await BotNotification().send_notification_by_wallet(
            wallet=request.wallet,
            notification_type=NotificationTypes.REQUEST,
            text_key=f'notification_request_update_state_{next_state}',
            request_id=request.id,
        )
        await self.create_action(
            model=request,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'type': 'confirmation',
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
            notification_type=NotificationTypes.REQUEST,
            text_key=f'notification_request_update_name',
            request_id=request.id,
            name=name,
        )
        await self.create_action(
            model=request,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'type': 'name',
                'name': name,
            },
        )
        return {}

    @session_required()
    async def update_cancellation(
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
                    'action': f'Update name',
                },
            ),
        )

        await self.create_action(
            model=request,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'type': 'cancellation',
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
                notification_type=NotificationTypes.ORDER,
                text_key='notification_order_update_state',
                order_id=order.id,
                state=OrderStates.CANCELED,
            )
            await bot_notification.send_notification_by_wallet(
                wallet=order.requisite.wallet,
                notification_type=NotificationTypes.ORDER,
                text_key='notification_order_update_state',
                order_id=order.id,
                state=OrderStates.CANCELED,
            )

    @staticmethod
    async def generate_request_dict(request: Request) -> dict:
        action = await ActionService().get_action(model=request, action=Actions.CREATE)
        date = action.datetime.strftime(settings.datetime_format)
        update_action = await ActionService().get_action(model=request, action=Actions.UPDATE)
        confirmation_delta = None
        if request.state == RequestStates.CONFIRMATION and update_action:
            time_now = datetime.datetime.now(tz=datetime.timezone.utc)
            time_update = update_action.datetime.replace(tzinfo=datetime.timezone.utc)
            time_delta = datetime.timedelta(minutes=settings.request_waiting_check)
            confirmation_delta = (time_delta - (time_now - time_update)).seconds
        input_method = None
        if request.input_method:
            input_method = await MethodService().generate_method_dict(method=request.input_method)
        output_requisite_data, output_method = None, None
        if request.output_requisite_data:
            output_requisite_data = await RequisiteDataService().generate_requisite_data_dict(
                requisite_data=request.output_requisite_data,
            )
            output_method = await MethodService().generate_method_dict(method=request.output_method)
        return {
            'id': request.id,
            'name': request.name,
            'wallet': await WalletService().generate_wallet_dict(wallet=request.wallet),
            'type': request.type,
            'state': request.state,
            'rate_decimal': request.rate_decimal,
            'difference': request.difference,
            'difference_rate': request.difference_rate,
            'commission': request.commission,
            'rate': request.rate,
            'input_method': input_method,
            'output_requisite_data': output_requisite_data,
            'output_method': output_method,
            'input_currency_value': request.input_currency_value,
            'input_rate': request.input_rate,
            'input_value': request.input_value,
            'output_value': request.output_value,
            'output_rate': request.output_rate,
            'output_currency_value': request.output_currency_value,
            'date': date,
            'confirmation_delta': confirmation_delta,
        }
