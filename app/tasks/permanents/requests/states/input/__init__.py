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

from app.db.models import RequestStates, OrderTypes, OrderStates, RequestTypes, WalletBanReasons, NotificationTypes
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.services import TransferSystemService, WalletBanService
from app.tasks.permanents.requests.logger import RequestLogger
from app.utils.bot.notification import BotNotification
from app.utils.calculations.requisites.need_value import calculations_requisites_need_input_currency_value

custom_logger = RequestLogger(prefix='request_state_input_check')


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.INPUT):
        request = await RequestRepository().get_by_id(id_=request.id)
        custom_logger.info(text='start check', request=request)
        continue_ = False
        for i in range(2):
            _need_currency_value = await calculations_requisites_need_input_currency_value(request=request)
            # check / change states
            if _need_currency_value:
                custom_logger.info(text=f'{request.state}->{RequestStates.INPUT_RESERVATION}', request=request)
                await RequestRepository().update(request, state=RequestStates.INPUT_RESERVATION)
                continue_ = True
                break
            if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.WAITING):
                custom_logger.info(text=f'{request.state}->{RequestStates.INPUT_RESERVATION}', request=request)
                await RequestRepository().update(request, state=RequestStates.INPUT_RESERVATION)
                continue_ = True  # Found waiting orders
                break
            if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.PAYMENT):
                continue_ = True  # Found payment orders
                break
            if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.CONFIRMATION):
                continue_ = True  # Found confirmation orders
                break
        if continue_:
            continue
        order_value_sum = 0
        difference_rate = request.difference_rate
        for order in await OrderRepository().get_list(request=request, type=OrderTypes.INPUT):
            if order.state == OrderStates.CANCELED:
                continue
            order_value_sum += order.value
        if order_value_sum != request.input_value:
            difference = order_value_sum - request.input_value
            await TransferSystemService().payment_difference(
                request=request,
                value=difference,
                from_banned_value=True,
            )
            difference_rate += difference
        await TransferSystemService().payment_commission(request=request, from_banned_value=True)
        next_state = RequestStates.OUTPUT_RESERVATION
        if request.type == RequestTypes.INPUT:
            next_state = RequestStates.COMPLETED
            await WalletBanService().create_related(
                wallet=request.wallet,
                value=-(request.input_value - request.commission),
                reason=WalletBanReasons.BY_ORDER,
            )
        custom_logger.info(text=f'{request.state}->{next_state}', request=request)
        await RequestRepository().update(
            request,
            state=next_state,
            difference_rate=difference_rate,
        )
        await BotNotification().send_notification_by_wallet(
            wallet=request.wallet,
            notification_type=NotificationTypes.REQUEST,
            text_key=f'notification_request_update_state_{next_state}',
            request_id=request.id,
        )
        await asyncio.sleep(1)
    await asyncio.sleep(5)


async def request_state_input_check():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
