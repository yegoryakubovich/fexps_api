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
import datetime
import logging

from app.db.models import RequestStates, Actions, Request, OrderStates
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.services import ActionService
from app.utils.service_addons.order import order_cancel_related
from config import settings

prefix = '[request_waiting_check]'


async def request_waiting_check():
    logging.critical('start request_waiting_check')
    while True:
        try:
            await run()
        except Exception as e:
            logging.error(f'{prefix}  Exception \n {e}')


async def run():
    time_now = datetime.datetime.now(datetime.UTC)
    for request in await RequestRepository().get_list_by_asc(state=RequestStates.WAITING):
        request_action = await ActionService().get_action(request, action=Actions.UPDATE)
        if not request_action:
            continue
        request_action_delta = time_now - request_action.datetime.replace(tzinfo=datetime.UTC)
        if request_action_delta >= datetime.timedelta(minutes=settings.request_waiting_check):
            await orders_update_state_to_canceled(request=request)
            await RequestRepository().update(request, state=RequestStates.CANCELED)
            logging.info(f'{prefix} Request.{request.id} state={RequestStates.CANCELED}')
        await asyncio.sleep(0.25)
    await asyncio.sleep(0.5)


async def orders_update_state_to_canceled(request: Request) -> None:
    for order in await OrderRepository().get_list(request=request):
        if order.state == OrderStates.CANCELED:
            continue
        await order_cancel_related(order=order)
        await OrderRepository().update(order, state=OrderStates.CANCELED)
        logging.info(f'{prefix} Request.{request.id}, Order.{order.id} state={OrderStates.CANCELED}')
