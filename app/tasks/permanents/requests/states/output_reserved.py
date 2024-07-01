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

from app.db.models import RequestStates, OrderTypes, OrderStates, Request, NotificationTypes
from app.repositories import OrderRepository, RequestRepository, RequisiteRepository
from app.services.order import OrderService
from app.services.transfer_system import TransferSystemService
from app.tasks.permanents.requests.logger import RequestLogger
from app.utils.bot.notification import BotNotification
from app.utils.calculations.request.states.output import request_check_state_output
from app.utils.calculations.requisites.find import calculate_requisite_output_by_currency_value, \
    calculate_requisite_output_by_value
from app.utils.calculations.requisites.need_value import calculations_requisites_output_need_currency_value, \
    calculations_requisites_output_need_value
from app.utils.value import value_to_int

custom_logger = RequestLogger(prefix='request_state_output_reserved_check')


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.OUTPUT_RESERVATION):
        custom_logger.info(text='start check', request=request)
        request = await RequestRepository().get_by_id(id_=request.id)
        currency = request.output_method.currency
        # get need values
        if request.rate_fixed:
            need_currency_value = await calculations_requisites_output_need_currency_value(request=request)
        else:
            need_value = await calculations_requisites_output_need_value(request=request)
            need_currency_value = round(need_value * request.output_rate / 10 ** request.rate_decimal)
        # check wait orders / complete state
        if need_currency_value < currency.div:
            active_order = False
            order_value = 0
            for order in await OrderRepository().get_list(type=OrderTypes.OUTPUT):
                if order.state == OrderStates.CANCELED:
                    continue
                elif order.state == OrderStates.COMPLETED:
                    order_value += order.value
                    continue
                active_order = True
                break
            if not active_order:
                difference = request.output_value
                if difference:
                    await TransferSystemService().payment_difference(
                        request=request,
                        value=difference,
                        from_banned_value=True,
                    )
                    await RequestRepository().update(
                        request,
                        output_value=request.output_value - difference,
                        difference_rate=request.difference_rate + difference,
                    )
                await request_check_state_output(request=request)
                continue
            waiting_orders = await OrderRepository().get_list(
                request=request,
                type=OrderTypes.OUTPUT,
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
                custom_logger.info(text=f'{request.state}->{RequestStates.OUTPUT}', request=request)
                await RequestRepository().update(request, state=RequestStates.OUTPUT)  # Started next state
                await BotNotification().send_notification_by_wallet(
                    wallet=request.wallet,
                    notification_type=NotificationTypes.REQUEST,
                    text_key=f'notification_request_update_state_{RequestStates.OUTPUT}',
                    request_id=request.id,
                )
            continue
        # create missing orders
        if request.rate_fixed:
            need_currency_value = await calculations_requisites_output_need_currency_value(request=request)
            custom_logger.info(text=f'create orders need_currency_value={need_currency_value}', request=request)
            result = await get_new_requisite(request=request, need_currency_value=need_currency_value)
            if result:
                difference_rate = request.difference_rate
                order_value_sum = 0
                for order in await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT):
                    if order.state == OrderStates.CANCELED:
                        continue
                    order_value_sum += order.value
                difference = request.output_value - order_value_sum
                if difference < 0:
                    difference = order_value_sum - request.output_value
                    await TransferSystemService().payment_difference(
                        request=request,
                        value=difference,
                        from_banned_value=True,
                    )
                    difference_rate += difference
                    await RequestRepository().update(request, difference_rate=difference_rate)
        else:
            need_value = await calculations_requisites_output_need_value(request=request)
            custom_logger.info(text=f'create orders need_value={need_value}', request=request)
            result = await get_new_requisite(request=request, need_value=need_value)
            if result:
                order_currency_value_sum = 0
                for order in await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT):
                    if order.state == OrderStates.CANCELED:
                        continue
                    order_currency_value_sum += order.currency_value
                await RequestRepository().update(request, output_currency_value=order_currency_value_sum)
    await asyncio.sleep(1)


async def get_new_requisite(
        request: Request,
        need_currency_value: int = None,
        need_value: int = None,
) -> bool:
    result = None
    if need_currency_value:
        result = await calculate_requisite_output_by_currency_value(
            method=request.output_method,
            currency_value=need_currency_value,
            process=True,
            request=request,
        )
    if need_value:
        result = await calculate_requisite_output_by_value(
            method=request.output_method,
            value=need_value,
            process=True,
            request=request,
        )
    if not result:
        return False
    for requisite_item in result.requisite_items:
        requisite = await RequisiteRepository().get_by_id(id_=requisite_item.requisite_id)
        rate_float = requisite_item.currency_value / requisite_item.value
        _rate = value_to_int(value=rate_float, decimal=request.rate_decimal, round_method=math.ceil)
        await OrderService().waited_order(
            request=request,
            requisite=requisite,
            currency_value=requisite_item.currency_value,
            value=requisite_item.value,
            rate=_rate,
            order_type=OrderTypes.OUTPUT,
        )
    return True


async def request_state_output_reserved_check():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
