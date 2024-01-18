#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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

from app.db.models import Currency, RequisiteTypes
from app.repositories.requisite import RequisiteRepository
from app.utils.calculations.orders.utils.hard import get_results_by_calc_requisites
from app.utils.calculations.orders.utils.simples import check_zero
from app.utils.schemes.calculations.orders import CalcOrderScheme, CalcRequisiteScheme


async def calc_output_currency_to_value(
        currency: Currency,
        currency_value: float,
) -> 'CalcOrderScheme':
    calc_requisites: List[CalcRequisiteScheme] = []
    for requisite in await RequisiteRepository().get_list_output_by_rate(
            type=RequisiteTypes.OUTPUT, currency=currency,
    ):
        if check_zero(currency_value, requisite.currency_value):
            continue
        if requisite.currency_value >= currency_value:
            suitable_currency_value = currency_value
        else:
            suitable_currency_value = requisite.currency_value
        suitable_value = math.ceil(suitable_currency_value / requisite.rate * 100)
        calc_requisites.append(CalcRequisiteScheme(
            requisite_id=requisite.id, currency_value=suitable_currency_value,
            value=suitable_value, rate=requisite.rate,
        ))
        currency_value = round(currency_value - suitable_currency_value)
    currency_value_result, value_result, rate_result = get_results_by_calc_requisites(
        calc_requisites=calc_requisites, type_='output',
    )
    return CalcOrderScheme(
        calc_requisites=calc_requisites, currency_value=currency_value_result, value=value_result, rate=rate_result,
    )
