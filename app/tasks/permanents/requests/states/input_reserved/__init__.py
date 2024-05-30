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

from app.db.models import RequestStates, OrderTypes, RequisiteTypes, OrderStates, Request, \
    RequisiteStates, NotificationTypes
from app.repositories import RequestRequisiteRepository
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.repositories.requisite import RequisiteRepository
from app.tasks.permanents.requests.logger import RequestLogger
from app.utils.bot.notification import BotNotification
from app.utils.calculations.request.basic import write_other
from app.utils.calculations.request.need_value import input_get_need_currency_value
from app.utils.calculations.simples import get_div_by_currency_value
from app.utils.service_addons.order import waited_order

custom_logger = RequestLogger(prefix='request_state_input_reserved_check')


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.INPUT_RESERVATION):
        request = await RequestRepository().get_by_id(id_=request.id)
        _from_value = request.input_currency_value_raw
        _need_currency_value = await input_get_need_currency_value(request=request, from_value=_from_value)
        # check / change states
        if not _need_currency_value:
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
                    notification_type=NotificationTypes.ORDER_CHANGE,
                    text_key='notification_order_update_state',
                    order_id=wait_order.id,
                    state=OrderStates.PAYMENT,
                )
                await bot_notification.send_notification_by_wallet(
                    wallet=wait_order.requisite.wallet,
                    notification_type=NotificationTypes.ORDER_CHANGE,
                    text_key='notification_order_update_state',
                    order_id=wait_order.id,
                    state=OrderStates.PAYMENT,
                )
            if not waiting_orders:
                custom_logger.info(text=f'{request.state}->{RequestStates.INPUT}', request=request)
                await write_other(request=request)
                await RequestRepository().update(request, state=RequestStates.INPUT)
                await BotNotification().send_notification_by_wallet(
                    wallet=request.wallet,
                    notification_type=NotificationTypes.REQUEST_CHANGE,
                    text_key='notification_request_update_state',
                    request_id=request.id,
                    state=RequestStates.INPUT,
                )
            continue
        # create missing orders
        await get_new_requisite_by_currency_value(request=request, need_currency_value=_need_currency_value)
        await asyncio.sleep(1)
    await asyncio.sleep(5)


async def get_new_requisite_by_currency_value(
        request: Request,
        need_currency_value: int,
) -> None:
    currency = request.input_method.currency
    for requisite in await RequisiteRepository().get_list_input_by_rate(
            type=RequisiteTypes.OUTPUT,
            state=RequisiteStates.ENABLE,
            currency=currency,
            in_process=False,
    ):
        await RequisiteRepository().update(requisite, in_process=True)
        if await RequestRequisiteRepository().check_blacklist(request=request, requisite=requisite):
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        rate_decimal, requisite_rate_decimal = request.rate_decimal, requisite.currency.rate_decimal
        requisite_rate = requisite.rate
        if rate_decimal != requisite_rate_decimal:
            requisite_rate = round(requisite.rate / 10 ** requisite_rate_decimal * 10 ** rate_decimal)
        _need_currency_value = need_currency_value
        # Zero check
        if 0 in [_need_currency_value, requisite.value]:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        # Min/Max check
        if requisite.currency_value_min and _need_currency_value < requisite.currency_value_min:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        if requisite.currency_value_max and _need_currency_value > requisite.currency_value_max:
            _need_currency_value = requisite.currency_value_max
        # Div check
        if _need_currency_value < currency.div:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        # Check max possible value
        if requisite.currency_value >= _need_currency_value:
            suitable_currency_value = _need_currency_value
        else:
            suitable_currency_value = requisite.currency_value
        # Check TRUE
        suitable_currency_value, suitable_value = get_div_by_currency_value(  # Rounded value
            currency_value=suitable_currency_value,
            div=currency.div,
            rate=requisite_rate,
            rate_decimal=rate_decimal,
            type_=OrderTypes.INPUT,
        )
        if not suitable_currency_value or not suitable_value:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        await waited_order(
            request=request,
            requisite=requisite,
            currency_value=suitable_currency_value,
            value=suitable_value,
            rate=requisite_rate,
            order_type=OrderTypes.INPUT,
        )
        need_currency_value = round(need_currency_value - suitable_currency_value)


async def request_state_input_reserved_check():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
