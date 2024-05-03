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

from app.db.models import Request, OrderTypes, OrderStates, Order, OrderRequest, OrderRequestStates, MessageRoles
from app.repositories.order import OrderRepository
from app.repositories.order_request import OrderRequestRepository
from app.repositories.request import RequestRepository
from app.utils.service_addons.order import order_cancel_related, order_edit_value_related
from app.utils.websockets.aiohttp import ConnectionManagerAiohttp


async def order_request_update_type_cancel(
        order_request: OrderRequest,
        state: str,
        canceled_reason: str,
        connections_manager_aiohttp: ConnectionManagerAiohttp,
):
    order: Order = order_request.order
    request: Request = order.request
    if state == OrderRequestStates.COMPLETED:
        if order.type == OrderTypes.INPUT:
            await RequestRepository().update(
                request,
                input_currency_value_raw=request.input_currency_value_raw - order.currency_value,
                input_currency_value=request.input_currency_value - order.currency_value,
                input_value_raw=request.input_value_raw - order.value,
                input_value=request.input_value - order.value,
            )
        elif order.type == OrderTypes.OUTPUT:
            await RequestRepository().update(
                request,
                output_currency_value_raw=request.output_currency_value_raw - order.currency_value,
                output_currency_value=request.output_currency_value - order.currency_value,
                output_value_raw=request.output_value_raw - order.value,
                output_value=request.output_value - order.value,
            )
        await order_cancel_related(order=order)
        await OrderRepository().update(
            order,
            state=OrderStates.CANCELED,
            canceled_reason=canceled_reason,
        )
        await OrderRequestRepository().update(order_request, state=state)
        await RequestRepository().update(order_request.order.request, rate_confirmed=False)
    elif state == OrderRequestStates.CANCELED:
        await OrderRequestRepository().update(order_request, state=state)
    await connections_manager_aiohttp.send(
        role=MessageRoles.SYSTEM,
        text=f'order_request_finished_{state}_{canceled_reason}',
    )


async def order_request_update_type_recreate(
        order_request: OrderRequest,
        state: str,
        canceled_reason: str,
        connections_manager_aiohttp: ConnectionManagerAiohttp,
):
    order: Order = order_request.order
    if state == OrderRequestStates.COMPLETED:
        await order_cancel_related(order=order)
        await OrderRepository().update(
            order,
            state=OrderStates.CANCELED,
            canceled_reason=canceled_reason,
        )
        await OrderRequestRepository().update(order_request, state=state)
        await RequestRepository().update(order_request.order.request, rate_confirmed=False)
    elif state == OrderRequestStates.CANCELED:
        await OrderRequestRepository().update(order_request, state=state)
    await connections_manager_aiohttp.send(
        role=MessageRoles.SYSTEM,
        text=f'order_request_finished_{state}_{canceled_reason}',
    )


async def order_request_update_type_update_value(
        order_request: OrderRequest,
        state: str,
        connections_manager_aiohttp: ConnectionManagerAiohttp,
):
    order: Order = order_request.order
    request: Request = order.request
    if state == OrderRequestStates.COMPLETED:
        currency_value = int(order_request.data['currency_value'])
        value = float(currency_value / order.rate * 10 ** order.request.rate_decimal)
        delta_currency_value = order.currency_value - currency_value
        value_method = math.floor if order.type == OrderTypes.INPUT else math.ceil
        delta_value = value_method(delta_currency_value / order.rate * 10 ** order.request.rate_decimal)
        if order.type == OrderTypes.INPUT:
            await RequestRepository().update(
                request,
                input_currency_value_raw=request.input_currency_value_raw - delta_currency_value,
                input_currency_value=request.input_currency_value - delta_currency_value,
                input_value_raw=request.input_value_raw - delta_value,
                input_value=request.input_value - delta_value,
            )
        elif order.type == OrderTypes.OUTPUT:
            await RequestRepository().update(
                request,
                output_currency_value_raw=request.output_currency_value_raw - delta_currency_value,
                output_currency_value=request.output_currency_value - delta_currency_value,
                output_value_raw=request.output_value_raw - delta_value,
                output_value=request.output_value - delta_value,
            )
        await order_edit_value_related(order=order, delta_value=delta_value, delta_currency_value=delta_currency_value)
        await OrderRepository().update(
            order,
            value=value,
            currency_value=currency_value,
        )
        await OrderRequestRepository().update(order_request, state=state)
        await RequestRepository().update(order_request.order.request, rate_confirmed=False)
    elif state == OrderRequestStates.CANCELED:
        await OrderRequestRepository().update(order_request, state=state)
    await connections_manager_aiohttp.send(
        role=MessageRoles.SYSTEM,
        text=f'order_request_finished_{state}',
    )
