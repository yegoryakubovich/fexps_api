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


from app.db.models import Request, OrderTypes, OrderStates, Order, OrderRequest, OrderRequestStates
from app.repositories.order import OrderRepository
from app.repositories.order_request import OrderRequestRepository
from app.repositories.request import RequestRepository
from app.utils.service_addons.order import order_cancel_related


async def order_request_update_type_cancel(order_request: OrderRequest, state: str, canceled_reason: str):
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


async def order_request_update_type_update_value(order_request: OrderRequest, state: str):
    if state == OrderRequestStates.COMPLETED:
        """CHANGE VALUE LOGIC"""
        await OrderRequestRepository().update(order_request, state=state)
        await RequestRepository().update(order_request.order.request, rate_confirmed=False)
    elif state == OrderRequestStates.CANCELED:
        await OrderRequestRepository().update(order_request, state=state)
