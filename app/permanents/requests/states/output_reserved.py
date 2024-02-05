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

from app.db.models import RequestStates, OrderTypes, OrderStates, RequisiteTypes
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.repositories.requisite import RequisiteRepository
from app.services import OrderService
from app.utils.calculations.hard import get_need_values_output, suitability_check_currency_value, \
    suitability_check_value


async def request_state_output_reserved_check():
    while True:
        try:
            await run()
        except:
            pass


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.OUTPUT_RESERVATION):
        currency = request.output_method.currency
        need_currency_value, need_value = await get_need_values_output(request=request,
                                                                       order_type=OrderTypes.OUTPUT)
        if not need_currency_value and not need_value:
            waiting_orders = await OrderRepository().get_list(
                request=request, type=OrderTypes.OUTPUT, state=OrderStates.WAITING,
            )
            for wait_order in waiting_orders:
                await OrderService().order_banned_value(wallet=request.wallet, value=wait_order.value)
                await OrderRepository().update(wait_order, state=OrderStates.RESERVE)
            if not waiting_orders:
                await RequestRepository().update(request, state=RequestStates.OUTPUT)  # Started next state
            continue
        for requisite in await RequisiteRepository().get_list_input_by_rate(
                type=RequisiteTypes.INPUT, currency=currency, in_process=False,
        ):
            await RequisiteRepository().update(requisite, in_process=True)
            if need_value:
                suitability_check_result = suitability_check_value(
                    need_value=need_value,
                    requisite=requisite,
                    currency_div=currency.div,
                    rate_decimal=request.rate_decimal,
                    order_type=OrderTypes.OUTPUT,
                )
            else:
                suitability_check_result = suitability_check_currency_value(
                    need_currency_value=need_currency_value,
                    requisite=requisite,
                    currency_div=currency.div,
                    rate_decimal=request.rate_decimal,
                    order_type=OrderTypes.OUTPUT,
                )
            if not suitability_check_result:
                await RequisiteRepository().update(requisite, in_process=False)
                continue
            suitable_currency_value, suitable_value = suitability_check_result
            wait_order = await OrderService().waited_order(
                request=request,
                requisite=requisite,
                currency_value=suitable_currency_value,
                value=suitable_value,
                rate=requisite.rate,
                order_type=OrderTypes.OUTPUT,
            )
            await OrderService().order_banned_value(wallet=request.wallet, value=wait_order.value)
            await OrderRepository().update(wait_order, state=OrderStates.RESERVE)
            await RequisiteRepository().update(requisite, in_process=False)
            await asyncio.sleep(0.125)
        await asyncio.sleep(0.25)
    await asyncio.sleep(0.5)
