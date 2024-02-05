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

from app.db.models import RequestStates, OrderTypes, RequisiteTypes, OrderStates
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.repositories.requisite import RequisiteRepository
from app.services import OrderService
from app.utils.calculations.hard import get_need_values_input, suitability_check_currency_value, suitability_check_value


async def request_state_input_reserved_check():
    while True:
        try:
            await run()
        except:
            pass


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.INPUT_RESERVATION):
        currency = request.input_method.currency
        need_currency_value, need_value = await get_need_values_input(request=request, order_type=OrderTypes.INPUT)
        if not need_currency_value and not need_value:
            waiting_orders = await OrderRepository().get_list(
                request=request, type=OrderTypes.INPUT, state=OrderStates.WAITING,
            )
            for wait_order in waiting_orders:
                await OrderRepository().update(wait_order, state=OrderStates.RESERVE)
            if not waiting_orders:
                await RequestRepository().update(request, state=RequestStates.INPUT)  # Started next state
            continue

        for requisite in await RequisiteRepository().get_list_input_by_rate(
                type=RequisiteTypes.OUTPUT, currency=currency, in_process=False,
        ):
            if need_currency_value:
                await RequisiteRepository().update(requisite, in_process=True)
                suitability_check_result = suitability_check_currency_value(
                    need_currency_value=need_currency_value,
                    requisite=requisite,
                    currency_div=currency.div,
                    rate_decimal=request.rate_decimal,
                    order_type=OrderTypes.INPUT,
                )
            else:
                suitability_check_result = suitability_check_value(
                    need_value=need_value,
                    requisite=requisite,
                    currency_div=currency.div,
                    rate_decimal=request.rate_decimal,
                    order_type=OrderTypes.INPUT,
                )
            if not suitability_check_result:
                await RequisiteRepository().update(requisite, in_process=False)
                continue
            suitable_currency_value, suitable_value = suitability_check_result
            await OrderService().waited_order(
                request=request,
                requisite=requisite,
                currency_value=suitable_currency_value,
                value=suitable_value,
                rate=requisite.rate,
                order_type=OrderTypes.INPUT,
            )
            need_currency_value = round(need_currency_value - suitable_currency_value)
            await asyncio.sleep(0.125)
        await asyncio.sleep(0.25)
    await asyncio.sleep(0.5)
