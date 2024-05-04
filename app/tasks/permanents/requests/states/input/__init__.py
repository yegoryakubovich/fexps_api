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

from app.db.models import RequestStates, OrderTypes, OrderStates, RequestTypes, WalletBanReasons, Request, Order
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.services import TransferSystemService, WalletBanService
from app.utils.calculations.request.need_value import input_get_need_currency_value


def send_log(
        text: str,
        prefix: str = 'request_state_input_check',
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
    for request in await RequestRepository().get_list(state=RequestStates.INPUT):
        request = await RequestRepository().get_by_id(id_=request.id)
        _from_value = request.input_currency_value_raw
        continue_ = False
        for i in range(2):
            _need_currency_value = await input_get_need_currency_value(request=request, from_value=_from_value)
            # check / change states
            if _need_currency_value:
                send_log(text=f'found _need_currency_value = {_need_currency_value}', request=request)
                send_log(text=f'{request.state}->{RequestStates.INPUT_RESERVATION}', request=request)
                await RequestRepository().update(request, state=RequestStates.INPUT_RESERVATION)
                continue_ = True
                break
            if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.WAITING):
                send_log(text=f'found waiting orders', request=request)
                send_log(text=f'{request.state}->{RequestStates.INPUT_RESERVATION}', request=request)
                await RequestRepository().update(request, state=RequestStates.INPUT_RESERVATION)
                continue_ = True  # Found waiting orders
                break
            if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.PAYMENT):
                send_log(text=f'found payment orders', request=request)
                continue_ = True  # Found payment orders
                break
            if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.CONFIRMATION):
                send_log(text=f'found confirmation orders', request=request)
                continue_ = True  # Found confirmation orders
                break
        if continue_:
            continue
        await TransferSystemService().payment_commission(request=request, from_banned_value=True)
        next_state = RequestStates.OUTPUT_RESERVATION
        if request.type == RequestTypes.INPUT:
            await WalletBanService().create_related(
                wallet=request.wallet,
                value=-(request.input_value - request.commission_value),
                reason=WalletBanReasons.BY_ORDER,
            )
            next_state = RequestStates.COMPLETED
        send_log(text=f'{request.state}->{next_state}', request=request)
        await RequestRepository().update(request, state=next_state)
        await asyncio.sleep(0.25)
    await asyncio.sleep(5)


async def request_state_input_check():
    send_log(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            send_log(text=f'Exception \n {e}', func=logging.critical)
