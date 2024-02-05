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


import asyncio

from app.db.models import RequestStates, OrderTypes, OrderStates
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.utils.calculations.hard import get_need_values_output


async def request_state_output_check():
    while True:
        try:
            await run()
        except:
            pass


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.OUTPUT):
        need_output_value, need_value = await get_need_values_output(request=request, order_type=OrderTypes.OUTPUT)
        if need_output_value or need_value:
            await RequestRepository().update(request, state=RequestStates.OUTPUT_RESERVATION)
            continue
        if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.WAITING):
            await RequestRepository().update(request, state=RequestStates.OUTPUT_RESERVATION)
            continue  # Found waiting orders
        if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.RESERVE):
            continue  # Found reserve orders
        if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.PAYMENT):
            continue  # Found payment orders
        if await OrderRepository().get_list(
                request=request, type=OrderTypes.OUTPUT, state=OrderStates.CONFIRMATION
        ):
            continue  # Found confirmation orders
        await RequestRepository().update(request, state=RequestStates.COMPLETED)
        await asyncio.sleep(0.25)
    await asyncio.sleep(0.5)