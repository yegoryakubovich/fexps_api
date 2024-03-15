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
from app.utils.calculations.request.difference import get_difference
from app.utils.calculations.request.need_value import output_get_need_currency_value

prefix = '[request_state_output_check]'


async def request_state_output_check():
    logging.critical('start request_state_output_check')
    while True:
        try:
            await run()
        except Exception as e:
            logging.error(f'{prefix}  Exception \n {e}')


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.OUTPUT):
        request = await RequestRepository().get_by_id(id_=request.id)
        if request.first_line == RequestFirstLine.OUTPUT_CURRENCY_VALUE:
            _from_value = request.first_line_value
        else:
            _from_value = request.output_currency_value_raw
        _need_currency_value = await output_get_need_currency_value(request=request, from_value=_from_value)
        # check wait orders / complete state
        if _need_currency_value:
            logging.debug(f'{prefix} request_{request.id} {request.state}->{RequestStates.OUTPUT_RESERVATION} (1)')
            await RequestRepository().update(request, state=RequestStates.OUTPUT_RESERVATION)
            continue
        if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.WAITING):
            logging.debug(f'{prefix} request_{request.id} {request.state}->{RequestStates.OUTPUT_RESERVATION} (2)')
            await RequestRepository().update(request, state=RequestStates.OUTPUT_RESERVATION)
            continue  # Found waiting orders
        if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.PAYMENT):
            continue  # Found payment orders
        if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.CONFIRMATION):
            continue  # Found confirmation orders
        logging.debug(f'{prefix} request_{request.id} {request.state}->{RequestStates.COMPLETED}')
        await RequestRepository().update(request, state=RequestStates.COMPLETED)
        await asyncio.sleep(0.25)
    await asyncio.sleep(0.5)
