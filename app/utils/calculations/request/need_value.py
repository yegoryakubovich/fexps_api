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


from app.db.models import Request, OrderStates, OrderTypes
from app.repositories.order import OrderRepository


# INPUT
async def input_get_need_currency_value(request: Request, from_value: int = None) -> int:
    result = from_value if from_value else request.first_line_value
    for order in await OrderRepository().get_list(request=request, type=OrderTypes.INPUT):
        if order.state == OrderStates.CANCELED:
            continue
        result = round(result - order.currency_value)
    return result


async def input_get_need_value(request: Request, from_value: int = None) -> int:
    result = from_value if from_value else request.first_line_value
    for order in await OrderRepository().get_list(request=request, type=OrderTypes.INPUT):
        if order.state == OrderStates.CANCELED:
            continue
        result = round(result - order.value)
    return result


# OUTPUT
async def output_get_need_currency_value(request: Request, from_value: int = None) -> int:
    result = from_value if from_value else request.first_line_value
    for order in await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT):
        if order.state == OrderStates.CANCELED:
            continue
        result = round(result - order.currency_value)
    return result


async def output_get_need_value(request: Request, from_value: int = None) -> int:
    result = from_value if from_value else request.first_line_value
    for order in await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT):
        if order.state == OrderStates.CANCELED:
            continue
        result = round(result - order.value)
    if result == request.difference_confirmed:
        return 0
    return result
