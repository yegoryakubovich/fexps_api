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


from app.db.models import Request, OrderTypes, OrderStates
from app.repositories import OrderRepository


async def calculations_requisites_output_need_value(request: Request) -> int:
    need_value = request.output_value
    for order in await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT):
        if order.state in [OrderStates.CANCELED]:
            continue
        need_value -= order.value
    return need_value
