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

from app.db.models import OrderTypes, OrderStates, Order, OrderRequest, OrderRequestStates, MessageRoles, \
    NotificationTypes
from app.repositories import OrderRepository, OrderRequestRepository
from app.utils.bot.notification import BotNotification
from app.utils.exceptions import RequisiteNotEnough
from app.utils.service_addons.order import order_cancel_related, order_edit_value_related, order_recreate_related
from app.utils.value import value_to_float
from app.utils.websockets.chat import ChatConnectionManagerAiohttp


async def order_request_update_type_cancel(
        order_request: OrderRequest,
        state: str,
        canceled_reason: str,
        connections_manager_aiohttp: ChatConnectionManagerAiohttp,
):
    from app.services.request import RequestService
    order = order_request.order
    if state == OrderRequestStates.COMPLETED:
        await order_cancel_related(order=order)
        await OrderRepository().update(
            order,
            state=OrderStates.CANCELED,
            canceled_reason=canceled_reason,
        )
        await RequestService().rate_fixed_off(request=order_request.order.request)
    await OrderRequestRepository().update(order_request, state=state)
    await connections_manager_aiohttp.send(
        role=MessageRoles.SYSTEM,
        text=f'order_request_finished_{order_request.type}_{state}_{canceled_reason}',
    )
    bot_notification = BotNotification()
    await bot_notification.send_notification_by_wallet(
        wallet=order.request.wallet,
        notification_type=NotificationTypes.ORDER,
        text_key=f'notification_order_request_finished_{order_request.type}_{state}_{canceled_reason}',
        order_id=order.id,
    )
    await bot_notification.send_notification_by_wallet(
        wallet=order.requisite.wallet,
        notification_type=NotificationTypes.ORDER,
        text_key=f'notification_order_request_finished_{order_request.type}_{state}_{canceled_reason}',
        order_id=order.id,
    )


async def order_request_update_type_recreate(
        order_request: OrderRequest,
        state: str,
        canceled_reason: str,
        connections_manager_aiohttp: ChatConnectionManagerAiohttp,
):
    from app.services.request import RequestService
    order: Order = order_request.order
    if state == OrderRequestStates.COMPLETED:
        await order_recreate_related(order=order)
        await OrderRepository().update(
            order,
            state=OrderStates.CANCELED,
            canceled_reason=canceled_reason,
        )
        await RequestService().rate_fixed_off(request=order_request.order.request)
    await OrderRequestRepository().update(order_request, state=state)
    await connections_manager_aiohttp.send(
        role=MessageRoles.SYSTEM,
        text=f'order_request_finished_{order_request.type}_{state}_{canceled_reason}',
    )
    bot_notification = BotNotification()
    await bot_notification.send_notification_by_wallet(
        wallet=order.request.wallet,
        notification_type=NotificationTypes.ORDER,
        text_key=f'notification_order_request_finished_{order_request.type}_{state}_{canceled_reason}',
        order_id=order.id,
    )
    await bot_notification.send_notification_by_wallet(
        wallet=order.requisite.wallet,
        notification_type=NotificationTypes.ORDER,
        text_key=f'notification_order_request_finished_{order_request.type}_{state}_{canceled_reason}',
        order_id=order.id,
    )


async def order_request_update_type_update_value(
        order_request: OrderRequest,
        state: str,
        connections_manager_aiohttp: ChatConnectionManagerAiohttp,
):
    from app.services.request import RequestService
    order = order_request.order
    requisite = order.requisite
    if state == OrderRequestStates.COMPLETED:
        currency_value = int(order_request.data['currency_value'])
        value = round(currency_value / order.rate * 10 ** order.request.rate_decimal)
        delta_currency_value = order.currency_value - currency_value
        delta_value = 0
        if order.type == OrderTypes.INPUT:
            delta_value = math.floor(delta_currency_value / order.rate * 10 ** order.request.rate_decimal)
        elif order.type == OrderTypes.OUTPUT:
            delta_value = math.ceil(delta_currency_value / order.rate * 10 ** order.request.rate_decimal)
        if requisite.currency_value < delta_currency_value:
            raise RequisiteNotEnough(
                kwargs={
                    'id_value': requisite.id,
                    'value': value_to_float(value=requisite.currency_value, decimal=requisite.currency.decimal),
                },
            )
        await order_edit_value_related(
            order=order,
            delta_value=delta_value,
            delta_currency_value=delta_currency_value,
        )
        await OrderRepository().update(
            order,
            value=value,
            currency_value=currency_value,
        )
        await RequestService().rate_fixed_off(request=order_request.order.request)
    await OrderRequestRepository().update(order_request, state=state)
    await connections_manager_aiohttp.send(
        role=MessageRoles.SYSTEM,
        text=f'order_request_finished_{order_request.type}_{state}',
    )
    bot_notification = BotNotification()
    await bot_notification.send_notification_by_wallet(
        wallet=order.request.wallet,
        notification_type=NotificationTypes.ORDER,
        text_key=f'notification_order_request_finished_{order_request.type}_{state}',
        order_id=order.id,
    )
    await bot_notification.send_notification_by_wallet(
        wallet=order.requisite.wallet,
        notification_type=NotificationTypes.ORDER,
        text_key=f'notification_order_request_finished_{order_request.type}_{state}',
        order_id=order.id,
    )
