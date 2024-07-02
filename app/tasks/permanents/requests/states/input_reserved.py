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
import math

from app.db.models import RequestStates, OrderTypes, OrderStates, NotificationTypes
from app.repositories import OrderRepository, RequestRepository, RequisiteRepository
from app.services.order import OrderService
from app.utils.bot.notification import BotNotification
from app.utils.calcs.request.states.input import request_check_state_input
from app.utils.calcs.requisites.find.input_by_currency_value import calcs_requisite_input_by_currency_value
from app.utils.calcs.requisites.find.input_by_value import calcs_requisite_input_by_value
from app.utils.calcs.requisites.need_value.input_currency_value import calcs_requisites_input_need_currency_value
from app.utils.calcs.requisites.need_value.input_value import calcs_requisites_input_need_value
from app.utils.value import value_to_int


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.INPUT_RESERVATION):
        logging.info(f'request #{request.id}    start check')
        request = await RequestRepository().get_by_id(id_=request.id)
        currency = request.input_method.currency
        # get need values
        if request.rate_fixed:
            need_currency_value = await calcs_requisites_input_need_currency_value(request=request)
        else:
            need_value = await calcs_requisites_input_need_value(request=request)
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
                logging.info(f'order #{wait_order.id}    {wait_order.state}->{OrderStates.PAYMENT}')
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
            logging.info(f'request #{request.id}   {request.state}->{RequestStates.INPUT}')
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
            need_currency_value = await calcs_requisites_input_need_currency_value(request=request)
        else:
            need_value = await calcs_requisites_input_need_value(request=request)
        result = None
        if need_currency_value:
            result = await calcs_requisite_input_by_currency_value(
                method=request.input_method,
                currency_value=need_currency_value,
                process=True,
                request=request,
            )
        if need_value:
            result = await calcs_requisite_input_by_value(
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
    logging.info(f'start request_state_input_reserved_check')
    while True:
        try:
            await run()
            await asyncio.sleep(2)
        except ValueError as e:
            logging.critical(f'Exception \n {e}')
