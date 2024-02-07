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
import logging
from datetime import datetime, timedelta

from app.db.models import RequestStates, Actions, Request, OrderStates
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.services import ActionService, OrderService
from config import settings


prefix = '[request_new_order_check]'


async def request_new_order_check():
    while True:
        try:
            await run()
        except Exception as e:
            logging.error(f'{prefix}  Exception \n {e}')


async def run():
    time_now = datetime.utcnow()
    for request in await RequestRepository().get_list_by_asc(state=RequestStates.WAITING):
        request_action = await ActionService().get_action(request, action=Actions.UPDATE)
        if time_now - request_action.datetime >= timedelta(minutes=settings.request_wait_minutes):
            await request_set_state_canceled(request=request)
        await asyncio.sleep(0.25)
    await asyncio.sleep(0.5)


async def request_set_state_canceled(request: Request) -> None:
    for order in await OrderRepository().get_list(request=request):
        if order.state == OrderStates.CANCELED:
            continue
        await OrderService().cancel_related(order=order)
        await OrderRepository().update(order, state=OrderStates.CANCELED)
    await RequestRepository().update(request, state=RequestStates.CANCELED)
