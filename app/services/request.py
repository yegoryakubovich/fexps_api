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
from typing import Optional

from app.db.models import Session, Request, Actions, RequestStates, RequestTypes, OrderStates, \
    NotificationTypes, RateTypes, OrderTypes, OrderRequestTypes
from app.repositories import WalletAccountRepository, OrderRepository, MethodRepository, RequisiteDataRepository, \
    CommissionPackValueRepository, RateRepository, RequestRepository, WalletRepository
from app.services.action import ActionService
from app.services.base import BaseService
from app.services.commission_pack_value import CommissionPackValueService
from app.services.method import MethodService
from app.services.order_request import OrderRequestService
from app.services.requisite_data import RequisiteDataService
from app.services.wallet import WalletService
from app.utils.bot.notification import BotNotification
from app.utils.calculations.request.rate.all import calculate_request_rate_all
from app.utils.calculations.request.rate.input import calculate_request_rate_input
from app.utils.calculations.request.rate.output import calculate_request_rate_output
from app.utils.decorators import session_required
from app.utils.exceptions import RequestRateNotFound
from app.utils.exceptions.request import RequestStateWrong, RequestStateNotPermission, RequestFoundOrders
from app.utils.service_addons.order import order_cancel_related
from app.utils.service_addons.wallet import wallet_check_permission
from config import settings


class RequestService(BaseService):
    model = Request

    """
    CLIENT
    """

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
        account = session.account
        start_value, end_value = input_value, output_value
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        input_method, output_method, output_requisite_data = None, None, None
        if input_method_id:
            input_method = await MethodRepository().get_by_id(id_=input_method_id)
        if output_requisite_data_id:
            output_requisite_data = await RequisiteDataRepository().get_by_id(id_=output_requisite_data_id)
            output_method = output_requisite_data.method
        input_method_name, output_method_name = '', ''
        if type_ == RequestTypes.INPUT:
            input_currency_value, input_value = start_value, end_value
            calculate = await calculate_request_rate_input(
                input_method=input_method,
                commission_pack=wallet.commission_pack,
                input_currency_value=input_currency_value,
                input_value=input_value,
            )
            if not calculate:
                raise RequestRateNotFound(
                    kwargs={
                        'input_method': input_method.name_text.value_default,
                        'output_method': settings.coin_name,
                    }
                )
        elif type_ == RequestTypes.OUTPUT:
            output_value, output_currency_value = start_value, end_value
            calculate = await calculate_request_rate_output(
                output_method=output_method,
                output_value=output_value,
                output_currency_value=output_currency_value,
            )
            if not calculate:
                raise RequestRateNotFound(
                    kwargs={
                        'input_method': settings.coin_name,
                        'output_method': output_method.name_text.value_default,
                    }
                )
            await WalletService().check_balance(wallet=wallet, value=calculate.output_value)
        else:
            input_currency_value, output_currency_value = start_value, end_value
            calculate = await calculate_request_rate_all(
                input_method=input_method,
                output_method=output_method,
                commission_pack=wallet.commission_pack,
                input_currency_value=input_currency_value,
                output_currency_value=output_currency_value,
            )
            if not calculate:
                raise RequestRateNotFound(
                    kwargs={
                        'input_method': input_method.name_text.value_default,
                        'output_method': output_method.name_text.value_default,
                    }
                )
        request = await RequestRepository().create(
            name=name,
            wallet=wallet,
            state=RequestStates.CONFIRMATION,
            type=type_,
            rate_decimal=calculate.rate_decimal,
            rate_fixed=True,
            difference=calculate.difference,
            difference_rate=0,
            commission=calculate.commission,
            rate=calculate.rate,
            input_method=input_method,
            output_requisite_data=output_requisite_data,
            output_method=output_method,
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
                'rate_decimal': calculate.rate_decimal,
                'rate_fixed': True,
                'difference': calculate.difference,
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
            wallet_id: int,
            type_: str,
            input_method_id: int = None,
            output_method_id: int = None,
    ) -> dict:
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        input_method, output_method = None, None
        if input_method_id:
            input_method = await MethodRepository().get_by_id(id_=input_method_id)
        if output_method_id:
            output_method = await MethodRepository().get_by_id(id_=output_method_id)
        input_rate, output_rate = None, None
        if type_ == RequestTypes.INPUT:  # INPUT
            input_rate = await RateRepository().get_actual(method=input_method, type=RateTypes.INPUT)
            if not input_rate:
                raise RequestRateNotFound(
                    kwargs={
                        'input_method': output_method.name_text.value_default,
                        'output_method': '',
                    }
                )
            input_rate = input_rate.rate
        elif type_ == RequestTypes.OUTPUT:  # OUTPUT
            output_rate = await RateRepository().get_actual(method=output_method, type=RateTypes.OUTPUT)
            if not output_rate:
                raise RequestRateNotFound(
                    kwargs={
                        'input_method': '',
                        'output_method': output_method.name_text.value_default,
                    }
                )
            output_rate = output_rate.rate
        else:  # ALL
            input_rate = await RateRepository().get_actual(method=input_method, type=RateTypes.INPUT)
            output_rate = await RateRepository().get_actual(method=output_method, type=RateTypes.OUTPUT)
            if not input_rate or not output_rate:
                raise RequestRateNotFound(
                    kwargs={
                        'input_method': input_method.name_text.value_default,
                        'output_method': output_method.name_text.value_default,
                    }
                )
            input_rate = input_rate.rate
            output_rate = output_rate.rate
        return {
            'wallet': wallet.id,
            'type': type_,
            'commissions_packs': [
                await CommissionPackValueService().generate_commission_pack_value_dict(commission_pack_value=cp_value)
                for cp_value in await CommissionPackValueRepository().get_list(commission_pack=wallet.commission_pack)
            ],
            'input_method': await MethodService().generate_method_dict(method=input_method),
            'input_rate': input_rate,
            'output_method': await MethodService().generate_method_dict(method=output_method),
            'output_rate': output_rate,
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

    @session_required(return_token=True)
    async def update_cancellation(
            self,
            session: Session,
            token: str,
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
                    'action': f'Cancellation',
                },
            ),
        )
        found_order_count = 0
        for order in await OrderRepository().get_list(request=request):
            if order.state in [OrderStates.COMPLETED, OrderStates.CANCELED]:
                continue
            found_order_count += 1
            if order.type == OrderTypes.INPUT and order.state == OrderStates.PAYMENT:
                found_order_count -= 1
                await OrderRequestService().create(
                    session=session,
                    token=token,
                    order_id=order.id,
                    type_=OrderRequestTypes.CANCEL,
                    value=None,
                )
        if found_order_count > 0:
            raise RequestFoundOrders(
                kwargs={
                    'id_value': request.id,
                },
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
        create_action = await ActionService().get_action(model=request, action=Actions.CREATE)
        date = create_action.datetime.strftime(settings.datetime_format)
        confirmation_delta = None
        if request.state == RequestStates.CONFIRMATION and create_action:
            time_now = datetime.datetime.now(tz=datetime.timezone.utc)
            time_create = create_action.datetime.replace(tzinfo=datetime.timezone.utc)
            time_delta = datetime.timedelta(minutes=settings.request_confirmation_check)
            confirmation_delta = (time_delta - (time_now - time_create)).seconds
        update_action = await ActionService().get_action(
            model=request,
            action=Actions.UPDATE,
            state=RequestStates.INPUT_RESERVATION,
        )
        rate_fixed_delta = None
        if request.rate_fixed and update_action:
            time_now = datetime.datetime.now(tz=datetime.timezone.utc)
            time_update = update_action.datetime.replace(tzinfo=datetime.timezone.utc)
            time_delta = datetime.timedelta(minutes=settings.request_rate_fixed_minutes)
            rate_fixed_delta = (time_delta - (time_now - time_update)).seconds
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
            'rate_fixed': request.rate_fixed,
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
            'rate_fixed_delta': rate_fixed_delta,
        }
