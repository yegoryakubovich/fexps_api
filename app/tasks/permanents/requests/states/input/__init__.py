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

from app.db.models import RequestStates, OrderTypes, OrderStates, RequestTypes, WalletBanReasons, RequestFirstLine
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.services import TransferSystemService, WalletBanService
from app.utils.calculations.request.need_value import input_get_need_currency_value

prefix = '[request_state_input_check]'


async def request_state_input_check():
    logging.critical('start request_state_input_check')
    while True:
        try:
            await run()
        except ValueError as e:
            logging.error(f'{prefix}  Exception \n {e}')


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.INPUT):
        request = await RequestRepository().get_by_id(id_=request.id)
        if request.first_line == RequestFirstLine.INPUT_CURRENCY_VALUE:
            _from_value = request.first_line_value
        else:
            _from_value = request.input_currency_value_raw
        _need_currency_value = await input_get_need_currency_value(request=request, from_value=_from_value)
        # check / change states
        if _need_currency_value:
            logging.debug(f'{prefix} request_{request.id} {request.state}->{RequestStates.INPUT_RESERVATION} (1)')
            await RequestRepository().update(request, state=RequestStates.INPUT_RESERVATION)
            continue
        if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.WAITING):
            logging.debug(f'{prefix} request_{request.id} {request.state}->{RequestStates.INPUT_RESERVATION} (2)')
            await RequestRepository().update(request, state=RequestStates.INPUT_RESERVATION)
            continue  # Found waiting orders
        if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.PAYMENT):
            continue  # Found payment orders
        if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.CONFIRMATION):
            continue  # Found confirmation orders
        await TransferSystemService().payment_commission(request=request, from_banned_value=True)
        next_state = RequestStates.OUTPUT_RESERVATION
        if request.type == RequestTypes.INPUT:
            await WalletBanService().create_related(
                wallet=request.wallet,
                value=-(request.input_value + request.commission_value),
                reason=WalletBanReasons.BY_ORDER,
            )
            next_state = RequestStates.COMPLETED
        logging.debug(f'{prefix} request_{request.id} {request.state}->{next_state}')
        await RequestRepository().update(request, state=next_state)
        await asyncio.sleep(0.25)
    await asyncio.sleep(0.5)
