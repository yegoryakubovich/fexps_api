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
import math

from app.db.models import RequestStates, OrderTypes, OrderStates, Request, \
    NotificationTypes
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.repositories.requisite import RequisiteRepository
from app.tasks.permanents.requests.logger import RequestLogger
from app.utils.bot.notification import BotNotification
from app.utils.calculations.requisites.find import calculate_requisite_input_by_currency_value
from app.utils.calculations.requisites.need_value import calculations_requisites_need_input_currency_value
from app.utils.service_addons.order import waited_order
from app.utils.value import value_to_int

custom_logger = RequestLogger(prefix='request_state_input_reserved_check')


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.INPUT_RESERVATION):
        request = await RequestRepository().get_by_id(id_=request.id)
        custom_logger.info(text='start check', request=request)
        need_currency_value = await calculations_requisites_need_input_currency_value(request=request)
        # check / change states
        if not need_currency_value:
            waiting_orders = await OrderRepository().get_list(
                request=request,
                type=OrderTypes.INPUT,
                state=OrderStates.WAITING,
            )
            for wait_order in waiting_orders:
                custom_logger.info(text=f'{wait_order.state}->{OrderStates.PAYMENT}', order=wait_order)
                await OrderRepository().update(wait_order, state=OrderStates.PAYMENT)
                bot_notification = BotNotification()
                await bot_notification.send_notification_by_wallet(
                    wallet=wait_order.request.wallet,
                    notification_type=NotificationTypes.ORDER,
                    text_key='notification_order_update_state',
                    order_id=wait_order.id,
                    state=OrderStates.PAYMENT,
                )
                await bot_notification.send_notification_by_wallet(
                    wallet=wait_order.requisite.wallet,
                    notification_type=NotificationTypes.ORDER,
                    text_key='notification_order_update_state',
                    order_id=wait_order.id,
                    state=OrderStates.PAYMENT,
                )
            if not waiting_orders:
                custom_logger.info(text=f'{request.state}->{RequestStates.INPUT}', request=request)
                await RequestRepository().update(request, state=RequestStates.INPUT)
                await BotNotification().send_notification_by_wallet(
                    wallet=request.wallet,
                    notification_type=NotificationTypes.REQUEST,
                    text_key=f'notification_request_update_state_{RequestStates.INPUT}',
                    request_id=request.id,
                )
            continue
        # create missing orders
        await get_new_requisite_by_currency_value(request=request, need_currency_value=need_currency_value)
        await asyncio.sleep(1)
    await asyncio.sleep(5)


async def get_new_requisite_by_currency_value(
        request: Request,
        need_currency_value: int,
) -> None:
    result = await calculate_requisite_input_by_currency_value(
        method=request.input_method,
        currency_value=need_currency_value,
        process=True,
        request=request,
    )
    if not result:
        return
    for requisite_item in result.requisite_items:
        requisite = await RequisiteRepository().get_by_id(id_=requisite_item.requisite_id)
        rate_float = requisite_item.currency_value / requisite_item.value
        _rate = value_to_int(value=rate_float, decimal=request.rate_decimal, round_method=math.floor)
        await waited_order(
            request=request,
            requisite=requisite,
            currency_value=requisite_item.currency_value,
            value=requisite_item.value,
            rate=_rate,
            order_type=OrderTypes.INPUT,
        )


async def request_state_input_reserved_check():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')