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
import logging
import math
from typing import List, Optional

from app.db.models import RequestStates, RequestTypes, OrderTypes, Request, Currency, RequisiteTypes, Actions
from app.repositories.request import RequestRepository
from app.repositories.requisite import RequisiteRepository
from app.services import OrderService
from app.services.base import BaseService
from app.tasks import celery_app
from app.utils.calculations.hard import get_need_values_input, get_need_values_output, get_results_by_calc_requisites
from app.utils.calculations.simples import get_div_values, check_zero
from app.utils.decorators.celery_async import celery_sync
from app.utils.schemes.calculations.orders import RequisiteTypeScheme, RequisiteScheme, AllRequisiteTypeScheme


@celery_app.task(name='request_state_loading_check')
@celery_sync
async def request_state_loading_check():
    for request in await RequestRepository().get_list(state=RequestStates.LOADING):
        if request.type == RequestTypes.ALL:
            result = await request_type_all(request=request)
            if not result:
                continue
            for input_requisite_scheme in result.input_requisites.requisites_list:
                await OrderService().reserve_order(
                    request=request, requisite_scheme=input_requisite_scheme, order_type=OrderTypes.INPUT,
                )
            for output_requisite_scheme in result.output_requisites.requisites_list:
                await OrderService().waited_order(
                    request=request, requisite_scheme=output_requisite_scheme, order_type=OrderTypes.OUTPUT,
                )
            await RequestRepository().update(
                request,
                state=RequestStates.WAITING,
                input_currency_value=result.input_currency_value,
                input_value=result.input_value,
                input_rate=result.input_requisites.rate,
                commission_value=result.commission_value,
                div_value=result.div_value,
                rate=result.rate,
                output_currency_value=result.output_currency_value,
                output_value=result.output_value,
                output_rate=result.output_requisites.rate,
            )
            await BaseService().create_action(
                model=request, action=Actions.UPDATE, parameters={},
            )
        elif request.type == RequestTypes.INPUT:
            result = await request_type_input(request=request)
            if not result:
                continue
            for requisite_scheme in result.requisites_list:
                await OrderService().reserve_order(
                    request=request, requisite_scheme=requisite_scheme, order_type=OrderTypes.INPUT,
                )
            await RequestRepository().update(
                request,
                state=RequestStates.WAITING,
                input_currency_value=result.currency_value,
                input_value=result.value,
                input_rate=result.rate,
                commission_value=result.commission_value,
                div_value=result.div_value,
                rate=result.rate,
            )
            await BaseService().create_action(
                model=request, action=Actions.UPDATE, parameters={},
            )
        elif request.type == RequestTypes.OUTPUT:
            result = await request_type_output(request=request)
            if not result:
                continue
            for requisite_scheme in result.requisites_list:
                await OrderService().waited_order(
                    request=request, requisite_scheme=requisite_scheme, order_type=OrderTypes.OUTPUT,
                )
            await RequestRepository().update(
                request,
                state=RequestStates.WAITING,
                commission_value=result.commission_value,
                div_value=result.div_value,
                rate=result.rate,
                output_currency_value=result.currency_value,
                output_value=result.value,
                output_rate=result.rate,
            )
            await BaseService().create_action(
                model=request, action=Actions.UPDATE, parameters={},
            )

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
        output_result = await request_type_output_value(
            request=request, currency=output_currency, need_value=input_result.value,
        )
        if not output_result:
            return
        rate_result = math.ceil(input_result.currency_value / output_result.currency_value * 100)
        return AllRequisiteTypeScheme(
            input_requisites=input_result,
            input_currency_value=input_result.currency_value,
            input_value=input_result.value,
            output_requisites=output_result,
            output_currency_value=output_result.currency_value,
            output_value=output_result.value,
            commission_value=round(input_result.commission_value + output_result.commission_value),
            div_value=round(input_result.div_value + output_result.div_value),
            rate=rate_result,
        )
    elif output_need_currency_value:
        output_result = await request_type_output_currency_value(
            request=request, currency=output_currency, need_currency_value=output_need_currency_value,
        )
        if not output_result:
            return
        input_result = await request_type_input_value(
            request=request, currency=input_currency, need_value=output_result.value,
        )
        if not input_result:
            return
        rate_result = math.ceil(input_result.currency_value / output_result.currency_value * 100)
        return AllRequisiteTypeScheme(
            input_requisites=input_result,
            input_currency_value=input_result.currency_value,
            input_value=input_result.value,
            output_requisites=output_result,
            output_currency_value=output_result.currency_value,
            output_value=output_result.value,
            commission_value=round(input_result.commission_value + output_result.commission_value),
            div_value=round(input_result.div_value + output_result.div_value),
            rate=rate_result,
        )


"""
INPUT
"""


async def request_type_input(request) -> Optional[RequisiteTypeScheme]:
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
) -> Optional[RequisiteTypeScheme]:
    requisites_scheme_list: List[RequisiteScheme] = []
    for requisite in await RequisiteRepository().get_list_input_by_rate(
            type=RequisiteTypes.OUTPUT, currency=currency, in_process=False,
    ):
        needed_currency_value = need_currency_value
        if check_zero(needed_currency_value, requisite.currency_value):
            continue
        if requisite.currency_value_min and needed_currency_value < requisite.currency_value_min:
            continue
        if requisite.currency_value_max and needed_currency_value > requisite.currency_value_max:
            needed_currency_value = requisite.currency_value_max

        if requisite.currency_value >= needed_currency_value:
            suitable_currency_value = needed_currency_value
        else:
            suitable_currency_value = requisite.currency_value
        suitable_currency_value, suitable_value = get_div_values(
            currency_value=suitable_currency_value, rate=requisite.rate, div=currency.div, type_=OrderTypes.INPUT,
        )
        if not suitable_currency_value or not suitable_value:
            continue
        requisites_scheme_list.append(RequisiteScheme(
            requisite_id=requisite.id,
            currency_value=suitable_currency_value,
            value=suitable_value,
            rate=requisite.rate,
        ))
        await RequisiteRepository().update(requisite, in_process=True)
        need_currency_value = round(need_currency_value - suitable_currency_value)
    if need_currency_value >= currency.div:
        for requisite_scheme in requisites_scheme_list:
            requisite = await RequisiteRepository().get_by_id(id_=requisite_scheme.requisite_id)
            await RequisiteRepository().update(requisite, in_process=True)
        return

    currency_value_result, value_result, rate_result, commission_value_result = await get_results_by_calc_requisites(
        request=request, requisites_scheme_list=requisites_scheme_list, type_='input',
    )
    return RequisiteTypeScheme(
        requisites_list=requisites_scheme_list,
        currency_value=currency_value_result,
        commission_value=commission_value_result,
        div_value=round(need_currency_value / rate_result * 100),
        value=value_result, rate=rate_result,
    )


async def request_type_input_value(
        request: Request, currency: Currency, need_value: int,
) -> Optional[RequisiteTypeScheme]:
    requisites_scheme_list: List[RequisiteScheme] = []
    rates_list: List[int] = []
    for requisite in await RequisiteRepository().get_list_input_by_rate(
            type=RequisiteTypes.OUTPUT, currency=currency, in_process=False,
    ):
        needed_value = need_value
        if check_zero(needed_value, requisite.currency_value):
            continue
        if requisite.value_min and needed_value < requisite.value_min:  # Меньше минимума
            continue
        if requisite.value_max and needed_value > requisite.value_max:  # Больше максимума
            needed_value = requisite.currency_value_max

        if round(needed_value * requisite.rate) < currency.div:
            continue
        if requisite.value >= needed_value:
            suitable_value = needed_value
        else:
            suitable_value = requisite.value
        suitable_currency_value, suitable_value = get_div_values(
            value=suitable_value, rate=requisite.rate, div=currency.div, type_=OrderTypes.INPUT,
        )
        if not suitable_currency_value or not suitable_value:
            continue

        requisites_scheme_list.append(RequisiteScheme(
            requisite_id=requisite.id,
            currency_value=suitable_currency_value,
            value=suitable_value,
            rate=requisite.rate,
        ))
        await RequisiteRepository().update(requisite, in_process=True)
        need_value = round(need_value - suitable_value)
        rates_list.append(requisite.rate)
    logging.info(rates_list)
    mean_rate = round(sum(rates_list) / len(rates_list))
    if round(need_value * mean_rate / 100) >= currency.div:
        for requisite_scheme in requisites_scheme_list:
            requisite = await RequisiteRepository().get_by_id(id_=requisite_scheme.requisite_id)
            await RequisiteRepository().update(requisite, in_process=True)
        return

    currency_value_result, value_result, rate_result, commission_value_result = await get_results_by_calc_requisites(
        request=request, requisites_scheme_list=requisites_scheme_list, type_='input',
    )
    return RequisiteTypeScheme(
        requisites_list=requisites_scheme_list,
        currency_value=currency_value_result,
        commission_value=commission_value_result,
        div_value=need_value,
        value=value_result,
        rate=rate_result,
    )


"""
OUTPUT
"""


async def request_type_output(request) -> Optional[RequisiteTypeScheme]:
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
) -> Optional[RequisiteTypeScheme]:
    requisites_scheme_list: List[RequisiteScheme] = []
    for requisite in await RequisiteRepository().get_list_output_by_rate(
            type=RequisiteTypes.INPUT, currency=currency, in_process=False,
    ):
        needed_currency_value = need_currency_value
        if check_zero(needed_currency_value, requisite.currency_value):
            continue
        if requisite.currency_value_min and needed_currency_value < requisite.currency_value_min:
            continue
        if requisite.currency_value_max and needed_currency_value > requisite.currency_value_max:
            needed_currency_value = requisite.currency_value_max

        if requisite.currency_value >= needed_currency_value:
            suitable_currency_value = needed_currency_value
        else:
            suitable_currency_value = requisite.currency_value
        suitable_currency_value, suitable_value = get_div_values(
            currency_value=suitable_currency_value, rate=requisite.rate, div=currency.div, type_=OrderTypes.OUTPUT,
        )
        if not suitable_currency_value or not suitable_value:
            continue

        requisites_scheme_list.append(RequisiteScheme(
            requisite_id=requisite.id,
            currency_value=suitable_currency_value,
            value=suitable_value,
            rate=requisite.rate,
        ))
        await RequisiteRepository().update(requisite, in_process=True)
        need_currency_value = round(need_currency_value - suitable_currency_value)
    if need_currency_value >= currency.div:
        for requisite_scheme in requisites_scheme_list:
            requisite = await RequisiteRepository().get_by_id(id_=requisite_scheme.requisite_id)
            await RequisiteRepository().update(requisite, in_process=True)
        return

    currency_value_result, value_result, rate_result, commission_value_result = await get_results_by_calc_requisites(
        request=request, requisites_scheme_list=requisites_scheme_list, type_='output',
    )
    return RequisiteTypeScheme(
        requisites_list=requisites_scheme_list,
        currency_value=currency_value_result,
        commission_value=commission_value_result,
        div_value=round(need_currency_value / rate_result * 100),
        value=value_result,
        rate=rate_result,
    )


async def request_type_output_value(
        request: Request, currency: Currency, need_value: int,
) -> Optional[RequisiteTypeScheme]:
    requisites_scheme_list: List[RequisiteScheme] = []
    rates_list: List[int] = []
    for requisite in await RequisiteRepository().get_list_output_by_rate(
            type=RequisiteTypes.INPUT, currency=currency, in_process=False,
    ):
        needed_value = need_value
        if check_zero(needed_value, requisite.currency_value):
            continue
        if requisite.value_min and needed_value < requisite.value_min:  # Меньше минимума
            continue
        if requisite.value_max and needed_value > requisite.value_max:  # Больше максимума
            needed_value = requisite.currency_value_max

        if round(needed_value * requisite.rate) < currency.div:
            continue
        if requisite.value >= needed_value:
            suitable_value = needed_value
        else:
            suitable_value = requisite.value
        suitable_currency_value, suitable_value = get_div_values(
            value=suitable_value, rate=requisite.rate, div=currency.div, type_=OrderTypes.OUTPUT,
        )
        if not suitable_currency_value or not suitable_value:
            continue

        requisites_scheme_list.append(RequisiteScheme(
            requisite_id=requisite.id, currency_value=suitable_currency_value,
            value=suitable_value, rate=requisite.rate,
        ))
        await RequisiteRepository().update(requisite, in_process=True)
        need_value = round(need_value - suitable_value)
        rates_list.append(requisite.rate)
    mean_rate = round(sum(rates_list) / len(rates_list))
    if round(need_value * mean_rate / 100) >= currency.div:
        for requisite_scheme in requisites_scheme_list:
            requisite = await RequisiteRepository().get_by_id(id_=requisite_scheme.requisite_id)
            await RequisiteRepository().update(requisite, in_process=True)
        return

    currency_value_result, value_result, rate_result, commission_value_result = await get_results_by_calc_requisites(
        request=request, requisites_scheme_list=requisites_scheme_list, type_='output',
    )
    return RequisiteTypeScheme(
        requisites_list=requisites_scheme_list,
        currency_value=currency_value_result,
        commission_value=commission_value_result,
        div_value=need_value,
        value=value_result,
        rate=rate_result,
    )
