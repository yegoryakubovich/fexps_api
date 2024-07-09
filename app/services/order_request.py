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

from app.db.models import Session, Actions, OrderRequest, OrderRequestTypes, OrderRequestStates, Order, OrderStates, \
    OrderCanceledReasons, MessageRoles, NotificationTypes, OrderTypes, RequestStates
from app.repositories import OrderRepository, OrderRequestRepository, WalletAccountRepository
from app.services.base import BaseService
from app.services.message import MessageService
from app.services.wallet import WalletService
from app.utils.bot.notification import BotNotification
from app.utils.decorators import session_required
from app.utils.exceptions import OrderStateWrong, OrderNotPermission, OrderRequestStateNotPermission, \
    OrderRequestAlreadyExists, RequisiteNotEnough
from app.utils.value import value_to_float


class OrderRequestService(BaseService):
    model = OrderRequest

    @session_required(return_token=True)
    async def create(
            self,
            session: Session,
            token: str,
            order_id: int,
            type_: str,
            value: Optional[int],
    ) -> dict:
        account = session.account
        order = await OrderRepository().get_by_id(id_=order_id)
        request = order.request
        wallet = order.request.wallet
        await WalletService().check_permission(
            account=account,
            wallets=[wallet],
            exception=OrderNotPermission(
                kwargs={
                    'field': 'Order',
                    'id_value': order.id
                },
            ),
        )
        need_states = [OrderStates.PAYMENT]
        if order.state not in need_states:
            raise OrderStateWrong(
                kwargs={
                    'id_value': order.id,
                    'state': order.state,
                    'need_state': f'/'.join(need_states),
                },
            )
        order_request, data = None, {}
        await self.check_have_order_request(order=order)
        bot_notification = BotNotification()
        if type_ == OrderRequestTypes.CANCEL:
            if order.type == OrderTypes.INPUT:
                if order.state in [OrderStates.WAITING, OrderStates.PAYMENT]:
                    order_request = await OrderRequestRepository().create(
                        wallet=wallet,
                        order=order,
                        type=type_,
                        state=OrderRequestStates.WAIT,
                        data=data,
                    )
                    await self.order_request_update_type_cancel(
                        order_request=order_request,
                        token=token,
                        state=OrderRequestStates.COMPLETED,
                        canceled_reason=OrderCanceledReasons.ONE_SIDED,
                    )
                    await MessageService().send_to_chat(
                        token=token,
                        order_id=order.id,
                        role=MessageRoles.SYSTEM,
                        text=f'order_request_create_{type_}',
                    )
        elif type_ == OrderRequestTypes.RECREATE:
            if order.type == OrderTypes.INPUT:
                if order.state in [OrderStates.WAITING, OrderStates.PAYMENT]:
                    order_request = await OrderRequestRepository().create(
                        wallet=wallet,
                        order=order,
                        type=type_,
                        state=OrderRequestStates.WAIT,
                        data=data,
                    )
                    await self.order_request_update_type_recreate(
                        order_request=order_request,
                        token=token,
                        state=OrderRequestStates.COMPLETED,
                        canceled_reason=OrderCanceledReasons.ONE_SIDED,
                    )
                    await MessageService().send_to_chat(
                        token=token,
                        order_id=order.id,
                        role=MessageRoles.SYSTEM,
                        text=f'order_request_create_{type_}',
                    )
        elif type_ == OrderRequestTypes.UPDATE_VALUE:
            data['currency_value'] = currency_value = value
            if currency_value == order.currency_value:
                return {}
            if order.type == OrderTypes.OUTPUT and currency_value > order.currency_value:
                example_value = round(currency_value / order.rate * 10 ** request.rate_decimal)
                await WalletService().check_balance(wallet=order.request.wallet, value=-example_value)
        if not order_request:
            order_request = await OrderRequestRepository().create(
                wallet=wallet,
                order=order,
                type=type_,
                state=OrderRequestStates.WAIT,
                data=data,
            )
            await MessageService().send_to_chat(
                token=token,
                order_id=order.id,
                role=MessageRoles.SYSTEM,
                text=f'order_request_create_{type_}',
            )
        await bot_notification.send_notification_by_wallet(
            wallet=order.request.wallet,
            notification_type=NotificationTypes.ORDER,
            text_key=f'notification_order_request_create_{type_}',
            order_id=order.id,
        )
        await bot_notification.send_notification_by_wallet(
            wallet=order.requisite.wallet,
            notification_type=NotificationTypes.ORDER,
            text_key=f'notification_order_request_create_{type_}',
            order_id=order.id,
        )
        await self.create_action(
            model=order_request,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'order_id': order_id,
                'type_': type_,
                'value': value,
            },
        )
        return {
            'id': order_request.id,
        }

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        order_request = await OrderRequestRepository().get_by_id(id_=id_)
        order = order_request.order
        await WalletService().check_permission(
            account=account,
            wallets=[order.request.wallet, order.requisite.wallet],
            exception=OrderNotPermission(
                kwargs={
                    'field': 'OrderRequest',
                    'id_value': order_request.id
                },
            ),
        )
        return {
            'order_request': await self.generate_order_request_dict(order_request=order_request),
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
            order_id: int,
    ) -> dict:
        account = session.account
        order = await OrderRepository().get_by_id(id_=order_id)
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
            'orders_requests': [
                await self.generate_order_request_dict(order_request=order_request)
                for order_request in await OrderRequestRepository().get_list(order=order)
            ]
        }

    @session_required(return_token=True)
    async def update(
            self,
            session: Session,
            token: str,
            id_: int,
            state: str
    ) -> dict:
        account = session.account
        order_request = await OrderRequestRepository().get_by_id(id_=id_, state=OrderRequestStates.WAIT)
        order = order_request.order
        wallet = order.requisite.wallet
        await WalletService().check_permission(
            account=account,
            wallets=[wallet],
            exception=OrderRequestStateNotPermission(
                kwargs={
                    'id_value': order_request.id,
                    'action': f'Change OrderRequest to state "{state}"',
                },
            ),
        )
        if order_request.type == OrderRequestTypes.CANCEL:
            await self.order_request_update_type_cancel(
                order_request=order_request,
                token=token,
                state=state,
                canceled_reason=OrderCanceledReasons.TWO_SIDED,
            )
        elif order_request.type == OrderRequestTypes.RECREATE:
            await self.order_request_update_type_recreate(
                order_request=order_request,
                token=token,
                state=state,
                canceled_reason=OrderCanceledReasons.TWO_SIDED,
            )
        elif order_request.type == OrderRequestTypes.UPDATE_VALUE:
            await self.order_request_update_type_update_value(
                order_request=order_request,
                token=token,
                state=state,
            )
        await OrderRequestRepository().update(order_request, state=state)
        await self.create_action(
            model=order_request,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'id': id_,
                'state': state,
            },
        )
        return {}

    @session_required(permissions=['orders'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        order_request = await OrderRequestRepository().get_by_id(id_=id_)
        await OrderRequestRepository().delete(order_request)
        await self.create_action(
            model=order_request,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )
        return {}

    @staticmethod
    async def check_have_order_request(order: Order) -> None:
        order_request = await OrderRequestRepository().get(order=order, state=OrderRequestStates.WAIT)
        if order_request:
            raise OrderRequestAlreadyExists(
                kwargs={
                    'id_': order_request.id,
                    'state': order_request.state,
                },
            )

    @staticmethod
    async def generate_order_request_dict(order_request: OrderRequest):
        return {
            'id': order_request.id,
            'wallet': await WalletService().generate_wallet_dict(wallet=order_request.wallet),
            'type': order_request.type,
            'state': order_request.state,
            'data': order_request.data,
        }

    @staticmethod
    async def order_request_update_type_cancel(
            order_request: OrderRequest,
            token: str,
            state: str,
            canceled_reason: str,
    ):
        from app.services.request import RequestService
        from app.services.order import OrderService
        order = order_request.order
        request = order.request
        requisite = order.requisite
        if state == OrderRequestStates.COMPLETED:
            await OrderService().order_cancel_related(order=order)
            await OrderRepository().update(
                order,
                state=OrderStates.CANCELED,
                canceled_reason=canceled_reason,
            )
            request_state = RequestStates.INPUT_RESERVATION
            if request.state == RequestStates.OUTPUT:
                request_state = RequestStates.OUTPUT_RESERVATION
            await RequestService().rate_fixed_off(request=request, state=request_state)
        await OrderRequestRepository().update(order_request, state=state)
        await MessageService().send_to_chat(
            token=token,
            order_id=order.id,
            role=MessageRoles.SYSTEM,
            text=f'order_request_finished_{order_request.type}_{state}_{canceled_reason}',
        )
        bot_notification = BotNotification()
        await bot_notification.send_notification_by_wallet(
            wallet=request.wallet,
            notification_type=NotificationTypes.ORDER,
            text_key=f'notification_order_request_finished_{order_request.type}_{state}_{canceled_reason}',
            order_id=order.id,
        )
        await bot_notification.send_notification_by_wallet(
            wallet=requisite.wallet,
            notification_type=NotificationTypes.ORDER,
            text_key=f'notification_order_request_finished_{order_request.type}_{state}_{canceled_reason}',
            order_id=order.id,
        )

    @staticmethod
    async def order_request_update_type_recreate(
            order_request: OrderRequest,
            token: str,
            state: str,
            canceled_reason: str,
    ):
        from app.services.request import RequestService
        from app.services.order import OrderService
        order = order_request.order
        request = order.request
        requisite = order.request
        if state == OrderRequestStates.COMPLETED:
            await OrderService().order_recreate_related(order=order)
            await OrderRepository().update(
                order,
                state=OrderStates.CANCELED,
                canceled_reason=canceled_reason,
            )
            request_state = RequestStates.INPUT_RESERVATION
            if request.state == RequestStates.OUTPUT:
                request_state = RequestStates.OUTPUT_RESERVATION
            await RequestService().rate_fixed_off(request=request, state=request_state)
        await OrderRequestRepository().update(order_request, state=state)
        await MessageService().send_to_chat(
            token=token,
            order_id=order.id,
            role=MessageRoles.SYSTEM,
            text=f'order_request_finished_{order_request.type}_{state}_{canceled_reason}',
        )
        bot_notification = BotNotification()
        await bot_notification.send_notification_by_wallet(
            wallet=request.wallet,
            notification_type=NotificationTypes.ORDER,
            text_key=f'notification_order_request_finished_{order_request.type}_{state}_{canceled_reason}',
            order_id=order.id,
        )
        await bot_notification.send_notification_by_wallet(
            wallet=requisite.wallet,
            notification_type=NotificationTypes.ORDER,
            text_key=f'notification_order_request_finished_{order_request.type}_{state}_{canceled_reason}',
            order_id=order.id,
        )

    @staticmethod
    async def order_request_update_type_update_value(
            order_request: OrderRequest,
            token: str,
            state: str,
    ):
        from app.services.request import RequestService
        from app.services.order import OrderService
        order = order_request.order
        request = order.request
        requisite = order.requisite
        if state == OrderRequestStates.COMPLETED:
            currency_value = int(order_request.data['currency_value'])
            value = round(currency_value / order.rate * 10 ** request.rate_decimal)
            delta_currency_value = order.currency_value - currency_value
            delta_value = 0
            if order.type == OrderTypes.INPUT:
                delta_value = math.floor(delta_currency_value / order.rate * 10 ** request.rate_decimal)
            elif order.type == OrderTypes.OUTPUT:
                delta_value = math.ceil(delta_currency_value / order.rate * 10 ** request.rate_decimal)
            if requisite.currency_value < delta_currency_value:
                raise RequisiteNotEnough(
                    kwargs={
                        'id_value': requisite.id,
                        'value': value_to_float(value=requisite.currency_value, decimal=requisite.currency.decimal),
                    },
                )
            await OrderService().order_edit_value_related(
                order=order,
                delta_value=delta_value,
                delta_currency_value=delta_currency_value,
            )
            await OrderRepository().update(order, value=value, currency_value=currency_value)
            request_state = RequestStates.INPUT_RESERVATION
            if request.state == RequestStates.OUTPUT:
                request_state = RequestStates.OUTPUT_RESERVATION
            await RequestService().rate_fixed_off(request=request, state=request_state)
        await OrderRequestRepository().update(order_request, state=state)
        await MessageService().send_to_chat(
            token=token,
            order_id=order.id,
            role=MessageRoles.SYSTEM,
            text=f'order_request_finished_{order_request.type}_{state}',
        )
        bot_notification = BotNotification()
        await bot_notification.send_notification_by_wallet(
            wallet=request.wallet,
            notification_type=NotificationTypes.ORDER,
            text_key=f'notification_order_request_finished_{order_request.type}_{state}',
            order_id=order.id,
        )
        await bot_notification.send_notification_by_wallet(
            wallet=requisite.wallet,
            notification_type=NotificationTypes.ORDER,
            text_key=f'notification_order_request_finished_{order_request.type}_{state}',
            order_id=order.id,
        )
