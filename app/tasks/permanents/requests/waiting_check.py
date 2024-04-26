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

from app.db.models import RequestStates, Actions, Request, OrderStates, Order
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.services import ActionService
from app.utils.service_addons.order import order_cancel_related
from config import settings


def send_log(
        text: str,
        prefix: str = 'request_waiting_check',
        func: callable = logging.info,
        request: Request = None,
        order: Order = None,
) -> None:
    log_list = [f'[{prefix}]']
    if order:
        log_list += [
            f'request.{order.request.id} ({order.request.type}:{order.request.state})',
            f'order.{order.id} ({order.type}:{order.state})',
        ]
    elif request:
        log_list += [
            f'request.{request.id} ({request.type}:{request.state})'
        ]
    log_list += [text]
    func(f' '.join(log_list))


async def run():
    time_now = datetime.datetime.now(datetime.UTC)
    for request in await RequestRepository().get_list_by_asc(state=RequestStates.WAITING):
        request_action = await ActionService().get_action(request, action=Actions.UPDATE)
        if not request_action:
            continue
        request_action_delta = time_now - request_action.datetime.replace(tzinfo=datetime.UTC)
        if request_action_delta >= datetime.timedelta(minutes=settings.request_waiting_check):
            send_log(text=f'{request.state}->{RequestStates.CANCELED}', request=request)
            await orders_update_state_to_canceled(request=request)
            await RequestRepository().update(request, state=RequestStates.CANCELED)
        await asyncio.sleep(0.25)
    await asyncio.sleep(0.5)


async def orders_update_state_to_canceled(request: Request) -> None:
    for order in await OrderRepository().get_list(request=request):
        if order.state == OrderStates.CANCELED:
            continue
        send_log(text=f'{order.state}->{OrderStates.CANCELED}', order=order)
        await order_cancel_related(order=order)
        await OrderRepository().update(order, state=OrderStates.CANCELED)


async def request_waiting_check():
    send_log(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            send_log(text=f'Exception \n {e}', func=logging.critical)
