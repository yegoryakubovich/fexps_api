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

from app.db.models import Session, Order, OrderTypes, OrderStates, Actions, MethodFieldTypes, OrderRequestStates, \
    MessageRoles, NotificationTypes, TransferTypes, Request, Requisite, WalletBanReasons, RequestRequisiteTypes, \
    RequestTypes
from app.repositories import WalletAccountRepository, TextRepository, OrderRequestRepository, OrderFileRepository, \
    FileKeyRepository, OrderRepository, RequestRepository, RequisiteRepository, WalletBanRequestRepository, \
    RequestRequisiteRepository, WalletBanRequisiteRepository
from app.services.base import BaseService
from app.services.currency import CurrencyService
from app.services.method import MethodService
from app.services.order_request import OrderRequestService
from app.services.request import RequestService
from app.services.requisite import RequisiteService
from app.services.transfer import TransferService
from app.services.wallet import WalletService
from app.services.wallet_ban import WalletBanService
from app.utils.bot.notification import BotNotification
from app.utils.calcs.request.states.input import request_check_state_input
from app.utils.calcs.request.states.output import request_check_state_output
from app.utils.decorators import session_required
from app.utils.exceptions.order import OrderNotPermission, OrderStateWrong, OrderStateNotPermission
from app.utils.websockets.chat import ChatConnectionManagerAiohttp


class OrderService(BaseService):
    model = Order

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        order = await OrderRepository().get_by_id(id_=id_)
        await WalletService().check_permission(
            account=account,
            wallets=[order.request.wallet, order.requisite.wallet],
            exception=OrderNotPermission(
                kwargs={
                    'field': 'Order',
                    'id_value': order.id
                },
            ),
        )
        return {
            'order': await self.generate_order_dict(order=order)
        }

    @session_required()
    async def get_all(
            self,
            session: Session,
            by_request: bool = False,
            by_requisite: bool = False,
            is_active: bool = False,
            is_finished: bool = False,
    ) -> dict:
        account = session.account
        wallets = [wa.wallet for wa in await WalletAccountRepository().get_list(account=account)]
        orders = []
        order_ids = []
        for wallet in wallets:
            if by_request:
                for request in await RequestRepository().get_list(wallet=wallet):
                    for order in await OrderRepository().get_list(request=request):
                        if not is_active and order.state not in [OrderStates.COMPLETED, OrderStates.CANCELED]:
                            continue
                        if not is_finished and order.state in [OrderStates.COMPLETED, OrderStates.CANCELED]:
                            continue
                        if order.id in order_ids:
                            continue
                        orders.append(order)
                        order_ids.append(order.id)
            if by_requisite:
                for requisite in await RequisiteRepository().get_list(wallet=wallet):
                    for order in await OrderRepository().get_list(requisite=requisite):
                        if not is_active and order.state not in [OrderStates.COMPLETED, OrderStates.CANCELED]:
                            continue
                        if not is_finished and order.state in [OrderStates.COMPLETED, OrderStates.CANCELED]:
                            continue
                        if order.id in order_ids:
                            continue
                        orders.append(order)
                        order_ids.append(order.id)
        return {
            'orders': [
                await self.generate_order_dict(order=order) for order in orders
            ]
        }

    @session_required()
    async def get_all_by_request(
            self,
            session: Session,
            request_id: int,
    ) -> dict:
        account = session.account
        request = await RequestRepository().get_by_id(id_=request_id)
        await WalletService().check_permission(
            account=account,
            wallets=[request.wallet],
            exception=OrderNotPermission(
                kwargs={
                    'field': 'Request',
                    'id_value': request.id
                },
            ),
        )
        return {
            'orders': [
                await self.generate_order_dict(order=order)
                for order in await OrderRepository().get_list(request=request)
            ]
        }

    @session_required()
    async def get_all_by_requisite(
            self,
            session: Session,
            requisite_id: int,
    ) -> dict:
        account = session.account
        requisite = await RequisiteRepository().get_by_id(id_=requisite_id)
        await WalletService().check_permission(
            account=account,
            wallets=[requisite.wallet],
            exception=OrderNotPermission(kwargs={'field': 'Requisite', 'id_value': requisite.id}),
        )
        return {
            'orders': [
                await self.generate_order_dict(order=order)
                for order in await OrderRepository().get_list(requisite=requisite)
            ]
        }

    @session_required(return_token=True)
    async def update_payment(
            self,
            session: Session,
            token: str,
            id_: int,
    ) -> dict:
        account = session.account
        need_state = OrderStates.CONFIRMATION
        next_state = OrderStates.PAYMENT
        order = await OrderRepository().get_by_id(id_=id_)
        if order.type == OrderTypes.INPUT:
            await WalletService().check_permission(
                account=account,
                wallets=[order.requisite.wallet],
                exception=OrderStateNotPermission(
                    kwargs={
                        'id_value': order.id,
                        'action': f'Update state to {next_state}',
                    }
                )
            )
        elif order.type == OrderTypes.OUTPUT:
            await WalletService().check_permission(
                account=account,
                wallets=[order.request.wallet],
                exception=OrderStateNotPermission(
                    kwargs={
                        'id_value': order.id,
                        'action': f'Update state to {next_state}',
                    }
                )
            )
        if order.state != need_state:
            raise OrderStateWrong(
                kwargs={
                    'id_value': order.id,
                    'state': order.state,
                    'need_state': need_state,
                },
            )
        connections_manager_aiohttp = ChatConnectionManagerAiohttp(token=token, order_id=order.id)
        await OrderRequestService().check_have_order_request(order=order)
        await OrderRepository().update(order, state=next_state)
        await connections_manager_aiohttp.send(role=MessageRoles.SYSTEM, text=f'order_update_state_{next_state}')
        bot_notification = BotNotification()
        await bot_notification.send_notification_by_wallet(
            wallet=order.request.wallet,
            notification_type=NotificationTypes.ORDER,
            account_id_black_list=[account.id],
            text_key='notification_order_update_state',
            order_id=order.id,
            state=next_state,
        )
        await bot_notification.send_notification_by_wallet(
            wallet=order.requisite.wallet,
            notification_type=NotificationTypes.ORDER,
            account_id_black_list=[account.id],
            text_key='notification_order_update_state',
            order_id=order.id,
            state=next_state,
        )
        await self.create_action(
            model=order,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'state': next_state,
            },
        )
        return {}

    @session_required(return_token=True)
    async def update_confirmation(
            self,
            session: Session,
            token: str,
            id_: int,
            input_fields: dict,
    ) -> dict:
        account = session.account
        need_state = OrderStates.PAYMENT
        next_state = OrderStates.CONFIRMATION
        order = await OrderRepository().get_by_id(id_=id_)
        if order.type == OrderTypes.INPUT:
            await WalletService().check_permission(
                account=account,
                wallets=[order.request.wallet],
                exception=OrderStateNotPermission(
                    kwargs={
                        'id_value': order.id,
                        'action': f'Update state to {next_state}',
                    }
                )
            )
        elif order.type == OrderTypes.OUTPUT:
            await WalletService().check_permission(
                account=account,
                wallets=[order.requisite.wallet],
                exception=OrderStateNotPermission(
                    kwargs={
                        'id_value': order.id,
                        'action': f'Update state to {next_state}',
                    }
                )
            )
        if order.state != need_state:
            raise OrderStateWrong(
                kwargs={
                    'id_value': order.id,
                    'state': order.state,
                    'need_state': need_state,
                },
            )
        await OrderRequestService().check_have_order_request(order=order)
        await MethodService().check_input_field(schema_input_fields=order.input_scheme_fields, fields=input_fields)
        await OrderRepository().update(order, state=next_state)
        connections_manager_aiohttp = ChatConnectionManagerAiohttp(token=token, order_id=order.id)
        for field_scheme in order.input_scheme_fields:
            field_key = field_scheme['key']
            field_value = input_fields.get(field_key)
            if not field_value:
                continue
            text = await TextRepository().get_by_key(key=field_scheme['name_text_key'])
            if field_scheme['type'] == MethodFieldTypes.IMAGE:
                for file_key in await FileKeyRepository().get_list(key=field_value):
                    if not file_key.file:
                        continue
                    await OrderFileRepository().create(order=order, file=file_key.file)
                await connections_manager_aiohttp.send(
                    role=MessageRoles.USER,
                    text=text.value_default,
                    files_key=field_value,
                )
                input_fields[field_key] = 'added'
            else:
                await connections_manager_aiohttp.send(
                    role=MessageRoles.USER,
                    text=f'{text.value_default}: {field_value}',
                )
        await OrderRepository().update(order, input_fields=input_fields)
        await connections_manager_aiohttp.send(role=MessageRoles.SYSTEM, text=f'order_update_state_{next_state}')
        bot_notification = BotNotification()
        await bot_notification.send_notification_by_wallet(
            wallet=order.request.wallet,
            notification_type=NotificationTypes.ORDER,
            account_id_black_list=[account.id],
            text_key='notification_order_update_state',
            order_id=order.id,
            state=next_state,
        )
        await bot_notification.send_notification_by_wallet(
            wallet=order.requisite.wallet,
            notification_type=NotificationTypes.ORDER,
            account_id_black_list=[account.id],
            text_key='notification_order_update_state',
            order_id=order.id,
            state=next_state,
        )
        await self.create_action(
            model=order,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'state': next_state,
                'input_fields': input_fields,
            },
        )
        return {}

    @session_required(return_token=True)
    async def update_completed(
            self,
            session: Session,
            token: str,
            id_: int,
    ) -> dict:
        account = session.account
        need_state = OrderStates.CONFIRMATION
        next_state = OrderStates.COMPLETED
        order = await OrderRepository().get_by_id(id_=id_)
        if order.type == OrderTypes.INPUT:
            await WalletService().check_permission(
                account=account,
                wallets=[order.requisite.wallet],
                exception=OrderStateNotPermission(
                    kwargs={
                        'id_value': order.id,
                        'action': f'Update state to {next_state}',
                    }
                )
            )
        elif order.type == OrderTypes.OUTPUT:
            await WalletService().check_permission(
                account=account,
                wallets=[order.request.wallet],
                exception=OrderStateNotPermission(
                    kwargs={
                        'id_value': order.id,
                        'action': f'Update state to {next_state}',
                    }
                )
            )
        if order.state != need_state:
            raise OrderStateWrong(
                kwargs={
                    'id_value': order.id,
                    'state': order.state,
                    'need_state': need_state,
                },
            )
        connections_manager_aiohttp = ChatConnectionManagerAiohttp(token=token, order_id=order.id)
        await OrderRequestService().check_have_order_request(order=order)
        await self.order_compete_related(order=order)
        await OrderRepository().update(order, state=next_state)
        await connections_manager_aiohttp.send(role=MessageRoles.SYSTEM, text=f'order_update_state_{next_state}')
        bot_notification = BotNotification()
        await bot_notification.send_notification_by_wallet(
            wallet=order.request.wallet,
            notification_type=NotificationTypes.ORDER,
            account_id_black_list=[account.id],
            text_key='notification_order_update_state',
            order_id=order.id,
            state=next_state,
        )
        await bot_notification.send_notification_by_wallet(
            wallet=order.requisite.wallet,
            notification_type=NotificationTypes.ORDER,
            account_id_black_list=[account.id],
            text_key='notification_order_update_state',
            order_id=order.id,
            state=next_state,
        )
        await self.create_action(
            model=order,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'state': next_state,
            },
        )
        if order.type == OrderTypes.INPUT:
            await request_check_state_input(request=order.request)
        elif order.type == OrderTypes.OUTPUT:
            await request_check_state_output(request=order.request)
        return {}

    @staticmethod
    async def generate_order_dict(order: Order) -> Optional[dict]:
        if not order:
            return
        method = order.request.input_method if order.type == OrderTypes.INPUT else order.request.output_method
        order_request = await OrderRequestRepository().get(order=order, state=OrderRequestStates.WAIT)
        if order_request:
            order_request = await OrderRequestService().generate_order_request_dict(order_request=order_request)
        return {
            'id': order.id,
            'type': order.type,
            'state': order.state,
            'canceled_reason': order.canceled_reason,
            'request': await RequestService().generate_request_dict(request=order.request),
            'requisite': await RequisiteService().generate_requisites_dict(requisite=order.requisite),
            'currency': await CurrencyService().generate_currency_dict(currency=order.requisite.currency),
            'currency_value': order.currency_value,
            'value': order.value,
            'rate': order.rate,
            'method': await MethodService().generate_method_dict(method=method),
            'requisite_scheme_fields': order.requisite_scheme_fields,
            'requisite_fields': order.requisite_fields,
            'input_scheme_fields': order.input_scheme_fields,
            'input_fields': order.input_fields,
            'order_request': order_request,
        }

    @staticmethod
    async def waited_order(
            request: Request,
            requisite: Requisite,
            currency_value: int,
            value: int,
            rate: int,
            order_type: str,
            order_state: str = OrderStates.WAITING,
    ) -> Order:
        await RequisiteRepository().update(
            requisite,
            currency_value=round(requisite.currency_value - currency_value),
            value=round(requisite.value - value),
            in_process=False,
        )
        requisite_scheme_fields, requisite_fields, input_scheme_fields, input_fields = None, None, None, None
        if order_type == OrderTypes.INPUT:
            requisite_scheme_fields = requisite.output_requisite_data.method.schema_fields
            requisite_fields = requisite.output_requisite_data.fields
            input_scheme_fields = requisite.output_requisite_data.method.schema_input_fields
        elif order_type == OrderTypes.OUTPUT:
            requisite_scheme_fields = request.output_requisite_data.method.schema_fields
            requisite_fields = request.output_requisite_data.fields
            input_scheme_fields = request.output_requisite_data.method.schema_input_fields
        return await OrderRepository().create(
            type=order_type,
            state=order_state,
            request=request,
            requisite=requisite,
            currency_value=currency_value,
            value=value,
            rate=rate,
            requisite_scheme_fields=requisite_scheme_fields,
            requisite_fields=requisite_fields,
            input_scheme_fields=input_scheme_fields,
            input_fields=input_fields,
        )

    @staticmethod
    async def order_cancel_related(order: Order) -> None:
        request = order.request
        currency = order.requisite.currency
        request_kwargs = {}
        if order.type == OrderTypes.INPUT:
            input_current_currency_value = request.input_currency_value - order.currency_value
            input_current_value = request.input_value - order.value
            current_commission = math.ceil(
                request.commission / request.input_currency_value * input_current_currency_value
            )
            request_kwargs.update(
                commission=current_commission,
                input_currency_value=input_current_currency_value,
                input_value=input_current_value,
            )
            if request.type in [RequestTypes.ALL]:
                output_current_value = input_current_value - current_commission
                output_current_currency_value = round(
                    output_current_value * request.output_rate / 10 ** request.rate_decimal
                )
                output_current_currency_value = math.floor(output_current_currency_value // currency.div) * currency.div
                request_kwargs.update(
                    output_currency_value=output_current_currency_value,
                    output_value=output_current_value,
                )
        elif order.type == OrderTypes.OUTPUT:
            output_current_currency_value = request.output_currency_value - order.currency_value
            output_current_value = request.output_value - order.value
            request_kwargs.update(
                output_currency_value=output_current_currency_value,
                output_value=output_current_value,
            )
            if order.state in [OrderStates.PAYMENT, OrderStates.CONFIRMATION]:
                wallet_ban = await WalletBanService().create_related(
                    wallet=request.wallet,
                    value=-order.value,
                    reason=WalletBanReasons.BY_REQUEST,
                )
                await WalletBanRequestRepository().create(wallet_ban=wallet_ban, request=request)
        await RequisiteRepository().update(
            order.requisite,
            currency_value=round(order.requisite.currency_value + order.currency_value),
            value=round(order.requisite.value + order.value),
        )
        await RequestRepository().update(request, **request_kwargs)

    @staticmethod
    async def order_recreate_related(order: Order) -> None:
        await RequestRequisiteRepository().create(
            request=order.request,
            requisite=order.requisite,
            type=RequestRequisiteTypes.BLACKLIST,
        )
        if order.type == OrderTypes.OUTPUT:
            if order.state in [OrderStates.PAYMENT, OrderStates.CONFIRMATION]:
                wallet_ban = await WalletBanService().create_related(
                    wallet=order.request.wallet,
                    value=-order.value,
                    reason=WalletBanReasons.BY_REQUEST,
                )
                await WalletBanRequestRepository().create(wallet_ban=wallet_ban, request=order.request)
        await RequisiteRepository().update(
            order.requisite,
            currency_value=round(order.requisite.currency_value + order.currency_value),
            value=round(order.requisite.value + order.value),
        )

    @staticmethod
    async def order_edit_value_related(
            order: Order,
            delta_value: int,
            delta_currency_value: int,
    ) -> None:
        request = order.request
        currency = order.requisite.currency
        request_kwargs = {}
        if order.type == OrderTypes.INPUT:
            current_input_currency_value = request.input_currency_value - delta_currency_value
            input_current_value = request.input_value - delta_value
            current_commission = math.ceil(
                request.commission / request.input_currency_value * current_input_currency_value
            )
            request_kwargs.update(
                commission=current_commission,
                input_currency_value=current_input_currency_value,
                input_value=input_current_value,
            )
            if request.type == RequestTypes.ALL:
                output_current_value = input_current_value - current_commission
                output_current_currency_value = round(
                    output_current_value * request.output_rate / 10 ** request.rate_decimal
                )
                output_current_currency_value = math.floor(output_current_currency_value // currency.div) * currency.div
                request_kwargs.update(
                    output_currency_value=output_current_currency_value,
                    output_value=output_current_value,
                )
        elif order.type == OrderTypes.OUTPUT:
            output_current_currency_value = request.output_currency_value - delta_currency_value
            output_current_value = request.output_value - delta_value
            request_kwargs.update(
                output_currency_value=output_current_currency_value,
                output_value=output_current_value,
            )
            if order.state in [OrderStates.PAYMENT, OrderStates.CONFIRMATION]:
                wallet_ban = await WalletBanService().create_related(
                    wallet=request.wallet,
                    value=-delta_value,
                    reason=WalletBanReasons.BY_REQUEST,
                )
                await WalletBanRequestRepository().create(wallet_ban=wallet_ban, request=request)
        await RequisiteRepository().update(
            order.requisite,
            currency_value=round(order.requisite.currency_value + delta_currency_value),
            value=round(order.requisite.value + delta_value),
        )
        await RequestRepository().update(request, **request_kwargs)

    @staticmethod
    async def order_compete_related(order: Order) -> None:
        if order.type == OrderTypes.INPUT:
            wallet_ban = await WalletBanService().create_related(
                wallet=order.requisite.wallet,
                value=-order.value,
                reason=WalletBanReasons.BY_REQUEST,
            )
            await WalletBanRequisiteRepository().create(wallet_ban=wallet_ban, requisite=order.requisite)
            await TransferService().create_transfer(
                type_=TransferTypes.IN_ORDER,
                wallet_from=order.requisite.wallet,
                wallet_to=order.request.wallet,
                value=order.value,
                order=order,
            )
            wallet_ban = await WalletBanService().create_related(
                wallet=order.request.wallet,
                value=order.value,
                reason=WalletBanReasons.BY_REQUEST,
            )
            await WalletBanRequestRepository().create(wallet_ban=wallet_ban, request=order.request)
        elif order.type == OrderTypes.OUTPUT:
            wallet_ban = await WalletBanService().create_related(
                wallet=order.request.wallet,
                value=-order.value,
                reason=WalletBanReasons.BY_REQUEST,
            )
            await WalletBanRequestRepository().create(wallet_ban=wallet_ban, request=order.request)
            await TransferService().create_transfer(
                type_=TransferTypes.IN_ORDER,
                wallet_from=order.request.wallet,
                wallet_to=order.requisite.wallet,
                value=order.value,
                order=order,
            )
