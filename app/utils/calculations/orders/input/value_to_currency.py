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


import math
from typing import List

from app.db.models import Currency, RequisiteTypes, Request
from app.repositories.requisite import RequisiteRepository
from app.utils.calculations.orders.utils.hard import get_results_by_calc_requisites
from app.utils.calculations.orders.utils.simples import check_zero, get_div_values
from app.utils.schemes.calculations.orders import CalcOrderScheme, CalcRequisiteScheme


async def calc_input_value_to_currency(
        request: Request,
        currency: Currency,
        value: int,
) -> 'CalcOrderScheme':
    calc_requisites: List[CalcRequisiteScheme] = []
    for requisite in await RequisiteRepository().get_list_input_by_rate(
            type=RequisiteTypes.OUTPUT, currency=currency,
    ):
        needed_value = value
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
            value=suitable_value, rate=requisite.rate, div=currency.div,
        )
        if not suitable_currency_value or not suitable_value:
            continue

        calc_requisites.append(CalcRequisiteScheme(
            requisite_id=requisite.id, currency_value=suitable_currency_value,
            value=suitable_value, rate=requisite.rate,
        ))
        value = round(value - suitable_value)
    if not calc_requisites:
        print(f'Founded requisites: {len(calc_requisites)}. STOPPED')
        raise

    currency_value_result, value_result, rate_result, commission_value_result = await  get_results_by_calc_requisites(
        request=request, calc_requisites=calc_requisites, type_='input',
    )
    return CalcOrderScheme(
        calc_requisites=calc_requisites,
        currency_value=currency_value_result, commission_value=commission_value_result,
        div_value=value,
        value=value_result, rate=rate_result,
    )
