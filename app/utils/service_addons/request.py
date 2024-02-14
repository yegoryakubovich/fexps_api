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
from app.db.models import Request, OrderTypes
from app.repositories.order import OrderRepository


async def request_get_need_value(
        request: Request,
        type_: OrderTypes,
        currency_value: int = None,
        value: int = None,
) -> int:
    if not value and not currency_value:
        return 0
    result = value or currency_value
    for order in await OrderRepository().get_list(request=request, type=type_):
        if value:  # value
            result -= order.value
        else:  # currency value
            result -= order.currency_value
    return result
