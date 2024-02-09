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

from app.db.models import RequestStates, OrderTypes, OrderStates, RequestTypes, WalletBanReasons
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.services import TransferSystemService, WalletBanService
from app.utils.calculations.request.need_value import check_need_value

prefix = '[request_state_output_check]'


async def request_state_output_check():
    while True:
        try:
            await run()
        except Exception as e:
            logging.error(f'{prefix}  Exception \n {e}')


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.OUTPUT):
        _need_value = await check_need_value(
            request=request,
            order_type=OrderTypes.OUTPUT,
            from_value=request.output_value_raw,
        )
        # check wait orders / complete state
        if _need_value:
            logging.debug(f'{prefix} request_{request.id} {request.state}->{RequestStates.OUTPUT_RESERVATION} (1)')
            await RequestRepository().update(request, state=RequestStates.OUTPUT_RESERVATION)
            continue
        if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.WAITING):
            logging.debug(f'{prefix} request_{request.id} {request.state}->{RequestStates.OUTPUT_RESERVATION} (2)')
            await RequestRepository().update(request, state=RequestStates.OUTPUT_RESERVATION)
            continue  # Found waiting orders
        if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.PAYMENT):
            continue  # Found payment orders
        if await OrderRepository().get_list(
                request=request,
                type=OrderTypes.OUTPUT,
                state=OrderStates.CONFIRMATION,
        ):
            continue  # Found confirmation orders
        await TransferSystemService().payment_div(request=request)
        if request.type == RequestTypes.INPUT:
            await WalletBanService().create_related(
                wallet=request.wallet,
                value=-request.input_value,
                reason=WalletBanReasons.BY_ORDER,
            )
        logging.debug(f'{prefix} request_{request.id} {request.state}->{RequestStates.COMPLETED}')
        await RequestRepository().update(request, state=RequestStates.COMPLETED)
        await asyncio.sleep(0.25)
    await asyncio.sleep(0.5)
