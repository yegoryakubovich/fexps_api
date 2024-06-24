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

from app.db.models import RequestStates, OrderTypes, OrderStates, NotificationTypes
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.services import TransferSystemService
from app.tasks.permanents.requests.logger import RequestLogger
from app.utils.bot.notification import BotNotification
from app.utils.calculations.requisites.need_value import calculations_requisites_need_output_currency_value, \
    calculations_requisites_need_output_value

custom_logger = RequestLogger(prefix='request_state_output_check')


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.OUTPUT):
        custom_logger.info(text='start check', request=request)
        request = await RequestRepository().get_by_id(id_=request.id)
        continue_ = False
        for i in range(2):
            if request.rate_fixed:
                need_currency_value = await calculations_requisites_need_output_currency_value(request=request)
                need_bool = bool(need_currency_value)
                need_bool = need_bool and need_currency_value >= request.output_method.currency.div
                need_bool = need_bool and need_currency_value > 0
            else:
                need_value = await calculations_requisites_need_output_value(request=request)
                need_bool = bool(need_value)
                need_bool = need_bool and need_value >= 100
                need_bool = need_bool and need_value > 0
            # check wait orders / complete state
            if need_bool:
                custom_logger.info(text=f'{request.state}->{RequestStates.OUTPUT_RESERVATION}', request=request)
                await RequestRepository().update(request, state=RequestStates.OUTPUT_RESERVATION)
                continue_ = True
                logging.critical(1)
                break
            if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.WAITING):
                custom_logger.info(text=f'{request.state}->{RequestStates.OUTPUT_RESERVATION}', request=request)
                await RequestRepository().update(request, state=RequestStates.OUTPUT_RESERVATION)
                continue_ = True
                logging.critical(2)
                break  # Found waiting orders
            if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.PAYMENT):
                continue_ = True
                logging.critical(3)
                break  # Found payment orders
            if await OrderRepository().get_list(
                    request=request,
                    type=OrderTypes.OUTPUT,
                    state=OrderStates.CONFIRMATION,
            ):
                logging.critical(4)
                continue_ = True
                break  # Found confirmation orders
        if continue_:
            continue
        order_value_sum = 0
        difference_rate = request.difference_rate
        for order in await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT):
            if order.state == OrderStates.CANCELED:
                continue
            order_value_sum += order.value
        if order_value_sum != request.output_value:
            difference = order_value_sum - request.output_value
            await TransferSystemService().payment_difference(
                request=request,
                value=difference,
                from_banned_value=True,
            )
            difference_rate += difference
        await TransferSystemService().payment_difference(
            request=request,
            value=request.difference,
            from_banned_value=True,
        )
        custom_logger.info(text=f'{request.state}->{RequestStates.COMPLETED}', request=request)
        await RequestRepository().update(request, state=RequestStates.COMPLETED)
        await BotNotification().send_notification_by_wallet(
            wallet=request.wallet,
            notification_type=NotificationTypes.REQUEST,
            text_key=f'notification_request_update_state_{RequestStates.COMPLETED}',
            request_id=request.id,
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
