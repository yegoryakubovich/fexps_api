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

from app.db.models import Request, RequestTypes, OrderTypes
from app.repositories.request import RequestRepository
from app.repositories.requisite import RequisiteRepository
from app.services import OrderService
from app.utils.calculations.orders import calc_all
from app.utils.calculations.orders.input import calc_input
from app.utils.calculations.orders.output import calc_output
from app.utils.schemes.calculations.orders import CalcRequisiteScheme
from app.utils.tasks.utils.hard import get_need_values_by_request


async def reserve_order(
        request: Request,
        calc_requisite: CalcRequisiteScheme,
        order_type: OrderTypes,
) -> None:
    requisite = await RequisiteRepository().get_by_id(id_=calc_requisite.requisite_id)
    await OrderService().create_related(
        order_type=order_type,
        request=request,
        requisite=requisite,
        currency_value=calc_requisite.currency_value,
        value=calc_requisite.value,
        rate=calc_requisite.rate,
    )


async def create_orders_input(request: Request) -> None:
    currency = request.input_method.currency
    need_input_value, need_value = await get_need_values_by_request(request=request, order_type=OrderTypes.INPUT)
    input_calc = await calc_input(currency=currency, currency_value=need_input_value, value=need_value)
    for calc_requisite in input_calc.calc_requisites:
        await reserve_order(request=request, calc_requisite=calc_requisite, order_type=OrderTypes.INPUT)
    await RequestRepository().update(
        request,
        input_value=input_calc.currency_value,
        input_rate=input_calc.rate,
        value=input_calc.value,
        rate=input_calc.rate,
    )


async def create_orders_output(request: Request):
    currency = request.output_method.currency
    need_output_value, need_value = await get_need_values_by_request(request=request, order_type=OrderTypes.OUTPUT)
    output_calc = await calc_output(currency=currency, currency_value=need_output_value, value=need_value)
    for calc_requisite in output_calc.calc_requisites:
        await reserve_order(request=request, calc_requisite=calc_requisite, order_type=OrderTypes.OUTPUT)
    await RequestRepository().update(
        request,
        input_value=output_calc.currency_value,
        input_rate=output_calc.rate,
        value=output_calc.value,
        rate=output_calc.rate,
    )


async def create_orders_all(request: Request):
    currency_input = request.input_method.currency
    currency_output = request.output_method.currency

    calc_requisites = await calc_all(
        currency_input=currency_input, currency_value_input=request.input_value,
        currency_output=currency_output, currency_value_output=request.output_value,
    )
    for calc_requisite_input in calc_requisites.input_calc.calc_requisites:
        await reserve_order(request=request, calc_requisite=calc_requisite_input, order_type=OrderTypes.INPUT)
    for calc_requisite_output in calc_requisites.output_calc.calc_requisites:
        await reserve_order(request=request, calc_requisite=calc_requisite_output, order_type=OrderTypes.OUTPUT)
    await RequestRepository().update(
        request,
        input_value=calc_requisites.input_currency_value, input_rate=calc_requisites.input_calc.rate,
        output_value=calc_requisites.output_currency_value, output_rate=calc_requisites.output_calc.rate,
        rate=calc_requisites.rate,
    )


async def create_orders(request: Request):
    if request.type == RequestTypes.INPUT:
        asyncio.create_task(create_orders_input(request=request), name=f'CREATE_ORDER_INPUT_{request.id}')
    elif request.type == RequestTypes.OUTPUT:
        asyncio.create_task(create_orders_output(request=request), name=f'CREATE_ORDER_OUTPUT_{request.id}')
    elif request.type == RequestTypes.ALL:
        asyncio.create_task(create_orders_input(request=request), name=f'CREATE_ORDER_INPUT_{request.id}')  # FIXME
