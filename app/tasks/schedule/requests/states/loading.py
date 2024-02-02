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
from typing import List, Optional

from app.db.models import RequestStates, RequestTypes, OrderTypes, Request, Currency, RequisiteTypes, Actions
from app.repositories.request import RequestRepository
from app.repositories.requisite import RequisiteRepository
from app.services import OrderService
from app.services.base import BaseService
from app.tasks import celery_app
from app.utils.calculations.hard import get_need_values_input, get_need_values_output, suitability_check_currency_value, \
    suitability_check_value
from app.utils.calculations.request import calc_request_value, request_model_calculation
from app.utils.decorators.celery_async import celery_sync
from app.utils.schemes.calculations.orders import RequisiteScheme, AllRequisiteTypeScheme


@celery_app.task()
def request_state_loading_check_smart_start():
    name = 'request_state_loading_check'
    actives = celery_app.control.inspect().active()
    for worker in actives:
        for task in actives[worker]:
            if task['name'] == name:
                return
    request_state_loading_check.apply_async()


@celery_app.task(name='request_state_loading_check')
@celery_sync
async def request_state_loading_check():
    for request in await RequestRepository().get_list(state=RequestStates.LOADING):
        if request.type == RequestTypes.ALL:  # ALL
            result = await request_type_all(request=request)
            if not result:
                continue
            for input_requisite_scheme in result.input_requisites:
                await OrderService().waited_order_by_scheme(
                    request=request, requisite_scheme=input_requisite_scheme, order_type=OrderTypes.INPUT,
                )
            for output_requisite_scheme in result.output_requisites:
                await OrderService().waited_order_by_scheme(
                    request=request, requisite_scheme=output_requisite_scheme, order_type=OrderTypes.OUTPUT,
                )
            await RequestRepository().update(request, state=RequestStates.WAITING)
            await BaseService().create_action(model=request, action=Actions.UPDATE)
        elif request.type == RequestTypes.INPUT:  # INPUT
            result_list = await request_type_input(request=request)
            if not result_list:
                continue
            for requisite_scheme in result_list:
                await OrderService().waited_order_by_scheme(
                    request=request, requisite_scheme=requisite_scheme, order_type=OrderTypes.INPUT,
                )
            await RequestRepository().update(request, state=RequestStates.WAITING)
            await BaseService().create_action(model=request, action=Actions.UPDATE)
        elif request.type == RequestTypes.OUTPUT:  # OUTPUT
            result_list = await request_type_output(request=request)
            if not result_list:
                continue
            for requisite_scheme in result_list:
                await OrderService().waited_order_by_scheme(
                    request=request, requisite_scheme=requisite_scheme, order_type=OrderTypes.OUTPUT,
                )
            await RequestRepository().update(request, state=RequestStates.WAITING)
            await BaseService().create_action(model=request, action=Actions.UPDATE)
        await request_model_calculation(request=request)

    request_state_loading_check.apply_async()


"""
ALL
"""


async def request_type_all(request) -> Optional[AllRequisiteTypeScheme]:
    input_currency = request.input_method.currency
    output_currency = request.output_method.currency
    input_need_currency_value, _ = await get_need_values_input(request=request, order_type=OrderTypes.INPUT)
    output_need_currency_value, _ = await get_need_values_output(request=request, order_type=OrderTypes.OUTPUT)
    if input_need_currency_value:
        input_result = await request_type_input_currency_value(
            request=request, currency=input_currency, need_currency_value=input_need_currency_value,
        )
        if not input_result:
            return
        _, input_value = await calc_request_value(request=request, requisites_list=input_result, type_='input')

        output_result = await request_type_output_value(
            request=request, currency=output_currency, need_value=input_value,
        )
        if not output_result:
            return
        return AllRequisiteTypeScheme(input_requisites=input_result, output_requisites=output_result)
    elif output_need_currency_value:
        output_result = await request_type_output_currency_value(
            request=request, currency=output_currency, need_currency_value=output_need_currency_value,
        )
        if not output_result:
            return
        _, output_value = await calc_request_value(request=request, requisites_list=output_result, type_='output')
        input_result = await request_type_input_value(
            request=request, currency=input_currency, need_value=output_value,
        )
        if not input_result:
            return
        return AllRequisiteTypeScheme(input_requisites=input_result, output_requisites=output_result)


"""
INPUT
"""


async def request_type_input(request) -> List[RequisiteScheme]:
    currency = request.input_method.currency
    need_currency_value, need_value = await get_need_values_input(request=request, order_type=OrderTypes.INPUT)
    if need_currency_value:
        return await request_type_input_currency_value(
            request=request, currency=currency, need_currency_value=need_currency_value,
        )
    elif need_value:
        return await request_type_input_value(
            request=request, currency=currency, need_value=need_value,
        )


async def request_type_input_currency_value(
        request: Request, currency: Currency, need_currency_value: int,
) -> List[RequisiteScheme]:
    requisites_scheme_list: List[RequisiteScheme] = []
    for requisite in await RequisiteRepository().get_list_input_by_rate(
            type=RequisiteTypes.OUTPUT, currency=currency, in_process=False,
    ):
        await RequisiteRepository().update(requisite, in_process=True)
        requisite_rate = round(requisite.rate / 10 ** requisite.currency.rate_decimal * 10 ** request.rate_decimal)
        suitability_check_result = suitability_check_currency_value(
            need_currency_value=need_currency_value,
            requisite=requisite,
            requisite_rate=requisite_rate,
            currency_div=currency.div,
            rate_decimal=request.rate_decimal,
            order_type=OrderTypes.INPUT,
        )
        if not suitability_check_result:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        suitable_currency_value, suitable_value = suitability_check_result
        requisites_scheme_list.append(RequisiteScheme(
            requisite_id=requisite.id,
            currency_value=suitable_currency_value,
            value=suitable_value,
            rate=requisite_rate,
        ))
        need_currency_value = round(need_currency_value - suitable_currency_value)
    if need_currency_value >= currency.div:
        for requisite_scheme in requisites_scheme_list:
            requisite = await RequisiteRepository().get_by_id(id_=requisite_scheme.requisite_id)
            await RequisiteRepository().update(requisite, in_process=False)
        return

    return requisites_scheme_list


async def request_type_input_value(
        request: Request, currency: Currency, need_value: int,
) -> List[RequisiteScheme]:
    requisites_scheme_list: List[RequisiteScheme] = []
    rates_list: List[int] = []
    for requisite in await RequisiteRepository().get_list_input_by_rate(
            type=RequisiteTypes.OUTPUT, currency=currency, in_process=False,
    ):
        await RequisiteRepository().update(requisite, in_process=True)
        requisite_rate = round(requisite.rate / 10 ** requisite.currency.rate_decimal * 10 ** request.rate_decimal)
        suitability_check_result = suitability_check_value(
            need_value=need_value,
            requisite=requisite,
            requisite_rate=requisite_rate,
            currency_div=currency.div,
            rate_decimal=request.rate_decimal,
            order_type=OrderTypes.INPUT,
        )
        if not suitability_check_result:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        suitable_currency_value, suitable_value = suitability_check_result
        requisites_scheme_list.append(RequisiteScheme(
            requisite_id=requisite.id,
            currency_value=suitable_currency_value,
            value=suitable_value,
            rate=requisite_rate,
        ))
        need_value = round(need_value - suitable_value)
        rates_list.append(requisite_rate)
    mean_rate = round(sum(rates_list) / len(rates_list))
    if round(need_value * mean_rate / 10 ** request.rate_decimal) >= currency.div:
        for requisite_scheme in requisites_scheme_list:
            requisite = await RequisiteRepository().get_by_id(id_=requisite_scheme.requisite_id)
            await RequisiteRepository().update(requisite, in_process=False)
        return

    return requisites_scheme_list


"""
OUTPUT
"""


async def request_type_output(request) -> List[RequisiteScheme]:
    currency = request.output_method.currency
    need_currency_value, need_value = await get_need_values_output(request=request, order_type=OrderTypes.OUTPUT)
    if need_currency_value:
        return await request_type_output_currency_value(
            request=request, currency=currency, need_currency_value=need_currency_value,
        )
    elif need_value:
        return await request_type_output_value(
            request=request, currency=currency, need_value=need_value,
        )


async def request_type_output_currency_value(
        request: Request, currency: Currency, need_currency_value: int,
) -> List[RequisiteScheme]:
    requisites_scheme_list: List[RequisiteScheme] = []
    for requisite in await RequisiteRepository().get_list_output_by_rate(
            type=RequisiteTypes.INPUT, currency=currency, in_process=False,
    ):
        await RequisiteRepository().update(requisite, in_process=True)
        requisite_rate = round(requisite.rate / 10 ** requisite.currency.rate_decimal * 10 ** request.rate_decimal)
        suitability_check_result = suitability_check_currency_value(
            need_currency_value=need_currency_value,
            requisite=requisite,
            requisite_rate=requisite_rate,
            currency_div=currency.div,
            rate_decimal=request.rate_decimal,
            order_type=OrderTypes.OUTPUT,
        )
        if not suitability_check_result:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        suitable_currency_value, suitable_value = suitability_check_result
        requisites_scheme_list.append(RequisiteScheme(
            requisite_id=requisite.id,
            currency_value=suitable_currency_value,
            value=suitable_value,
            rate=requisite_rate,
        ))
        await RequisiteRepository().update(requisite, in_process=True)
        need_currency_value = round(need_currency_value - suitable_currency_value)
    if need_currency_value >= currency.div:
        for requisite_scheme in requisites_scheme_list:
            requisite = await RequisiteRepository().get_by_id(id_=requisite_scheme.requisite_id)
            await RequisiteRepository().update(requisite, in_process=True)
        return

    return requisites_scheme_list


async def request_type_output_value(
        request: Request, currency: Currency, need_value: int,
) -> List[RequisiteScheme]:
    requisites_scheme_list: List[RequisiteScheme] = []
    rates_list: List[int] = []
    for requisite in await RequisiteRepository().get_list_output_by_rate(
            type=RequisiteTypes.INPUT, currency=currency, in_process=False,
    ):
        await RequisiteRepository().update(requisite, in_process=True)
        requisite_rate = round(requisite.rate / 10 ** requisite.currency.rate_decimal * 10 ** request.rate_decimal)
        suitability_check_result = suitability_check_value(
            need_value=need_value,
            requisite=requisite,
            requisite_rate=requisite_rate,
            currency_div=currency.div,
            rate_decimal=request.rate_decimal,
            order_type=OrderTypes.OUTPUT,
        )
        if not suitability_check_result:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        suitable_currency_value, suitable_value = suitability_check_result
        requisites_scheme_list.append(RequisiteScheme(
            requisite_id=requisite.id,
            currency_value=suitable_currency_value,
            value=suitable_value,
            rate=requisite_rate,
        ))
        await RequisiteRepository().update(requisite, in_process=True)
        need_value = round(need_value - suitable_value)
        rates_list.append(requisite.rate)
    mean_rate = round(sum(rates_list) / len(rates_list))
    if round(need_value * mean_rate / 10 ** request.rate_decimal) >= currency.div:
        for requisite_scheme in requisites_scheme_list:
            requisite = await RequisiteRepository().get_by_id(id_=requisite_scheme.requisite_id)
            await RequisiteRepository().update(requisite, in_process=True)
        return

    return requisites_scheme_list
