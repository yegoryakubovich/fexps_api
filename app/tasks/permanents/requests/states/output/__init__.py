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

from app.db.models import RequestStates, OrderTypes, OrderStates, RequestTypes, NotificationTypes
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.tasks.permanents.requests.logger import RequestLogger
from app.utils.bot.notification import BotNotification
from app.utils.calculations.request.need_value import output_get_need_value

custom_logger = RequestLogger(prefix='request_state_output_check')


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.OUTPUT):
        request = await RequestRepository().get_by_id(id_=request.id)
        if request.type == RequestTypes.ALL:
            if request.rate_confirmed:
                _from_value = request.output_value_raw
            else:
                _from_value = request.input_value
        else:
            _from_value = request.output_value_raw
        continue_ = False
        for i in range(2):
            _need_value = await output_get_need_value(request=request, from_value=_from_value)
            # check wait orders / complete state
            if _need_value:
                custom_logger.info(text=f'found _need_value={_need_value}', request=request)
                custom_logger.info(text=f'{request.state}->{RequestStates.OUTPUT_RESERVATION}', request=request)
                await RequestRepository().update(request, state=RequestStates.OUTPUT_RESERVATION)
                continue_ = True
                break
            if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.WAITING):
                custom_logger.info(text=f'found waiting orders', request=request)
                custom_logger.info(text=f'{request.state}->{RequestStates.OUTPUT_RESERVATION}', request=request)
                await RequestRepository().update(request, state=RequestStates.OUTPUT_RESERVATION)
                continue_ = True
                break  # Found waiting orders
            if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.PAYMENT):
                custom_logger.info(text=f'found payment orders', request=request)
                continue_ = True
                break  # Found payment orders
            if await OrderRepository().get_list(
                    request=request,
                    type=OrderTypes.OUTPUT,
                    state=OrderStates.CONFIRMATION,
            ):
                custom_logger.info(text=f'found confirmation orders', request=request)
                continue_ = True
                break  # Found confirmation orders
        if continue_:
            continue
        custom_logger.info(text=f'{request.state}->{RequestStates.COMPLETED}', request=request)
        await RequestRepository().update(request, state=RequestStates.COMPLETED)
        await BotNotification().send_notification_by_wallet(
            wallet=request.wallet,
            notification_type=NotificationTypes.REQUEST_CHANGE,
            text_key='notification_request_update_state',
            request_id=request.id,
            state=RequestStates.COMPLETED,
        )
        await asyncio.sleep(1)
    await asyncio.sleep(5)


async def request_state_output_check():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
