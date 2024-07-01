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
from app.repositories import OrderRepository, RequestRepository, RequisiteRepository
from app.services.order import OrderService
from app.tasks.permanents.requests.logger import RequestLogger
from app.utils.bot.notification import BotNotification
from app.utils.calculations.request.states.input import request_check_state_input
from app.utils.calculations.requisites.find import calculate_requisite_input_by_currency_value, \
    calculate_requisite_input_by_value
from app.utils.calculations.requisites.need_value import calculations_requisites_input_need_currency_value, \
    calculations_requisites_input_need_value
from app.utils.value import value_to_int

custom_logger = RequestLogger(prefix='request_state_input_reserved_check')


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.INPUT_RESERVATION):
        custom_logger.info(text='start check', request=request)
        request = await RequestRepository().get_by_id(id_=request.id)
        currency = request.input_method.currency
        # get need values
        if request.rate_fixed:
            need_currency_value = await calculations_requisites_input_need_currency_value(request=request)
        else:
            need_value = await calculations_requisites_input_need_value(request=request)
            need_currency_value = round(need_value * request.input_rate / 10 ** request.rate_decimal)
        # check / change states
        if need_currency_value < currency.div:
            if not await OrderRepository().get_list(type=OrderTypes.INPUT):
                await request_check_state_input(request=request)
                continue
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
        need_currency_value, need_value = None, None
        if request.rate_fixed:
            need_currency_value = await calculations_requisites_input_need_currency_value(request=request)
        else:
            need_value = await calculations_requisites_input_need_value(request=request)
        await get_new_requisite(request=request, need_currency_value=need_currency_value, need_value=need_value)

    await asyncio.sleep(1)


async def get_new_requisite(
        request: Request,
        need_currency_value: int = None,
        need_value: int = None,
) -> None:
    result = None
    if need_currency_value:
        result = await calculate_requisite_input_by_currency_value(
            method=request.input_method,
            currency_value=need_currency_value,
            process=True,
            request=request,
        )
    if need_value:
        result = await calculate_requisite_input_by_value(
            method=request.input_method,
            value=need_value,
            process=True,
            request=request,
        )
    if not result:
        return
    for requisite_item in result.requisite_items:
        requisite = await RequisiteRepository().get_by_id(id_=requisite_item.requisite_id)
        rate_float = requisite_item.currency_value / requisite_item.value
        _rate = value_to_int(value=rate_float, decimal=request.rate_decimal, round_method=math.floor)
        await OrderService().waited_order(
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
