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
from typing import Optional

from app.db.models import Method, RequisiteStates, RequisiteTypes, RateTypes, Requisite
from app.repositories import RequisiteRepository
from app.utils.calcs.requisites.check_empty import calcs_requisite_check_empty
from app.utils.value import value_to_int, value_to_float


async def calcs_requisite_suitable_from_value(
        requisite: Requisite,
        need_value: int,
) -> Optional[tuple[int, int]]:
    if requisite.is_flex:
        return
    value = need_value
    if value > requisite.value:
        value = requisite.value
    rate_float = value_to_float(value=requisite.rate, decimal=requisite.currency.rate_decimal)
    currency_value = value * rate_float // requisite.currency.div * requisite.currency.div
    if requisite.currency_value_max and currency_value > requisite.currency_value_max:
        value = requisite.currency_value_max
    if requisite.type == RateTypes.INPUT:
        value = math.ceil(currency_value / rate_float)
    elif requisite.type == RateTypes.OUTPUT:
        value = math.floor(currency_value / rate_float)
    if not value or not currency_value:
        return
    return currency_value, value


async def calcs_requisite(
        method: Method,
        rate_type: str,
        value: int,
) -> Optional[int]:
    need_value = value
    result_currency_value, result_value = 0, 0
    if rate_type == RateTypes.INPUT:
        requisite_params = {'type': RequisiteTypes.OUTPUT, 'output_method': method, 'state': RequisiteStates.ENABLE}
        round_method = math.ceil
        requisites = await RequisiteRepository().get_list_output_by_rate(**requisite_params)
    else:
        requisite_params = {'type': RequisiteTypes.INPUT, 'input_method': method, 'state': RequisiteStates.ENABLE}
        round_method = math.floor
        requisites = await RequisiteRepository().get_list_input_by_rate(**requisite_params)
    for requisite in requisites:
        # Check need_value
        if not need_value:
            break
        # Check balance
        if await calcs_requisite_check_empty(requisite=requisite):
            continue
        # Find suitable value
        suitable_result = await calcs_requisite_suitable_from_value(requisite=requisite, need_value=need_value)
        if not suitable_result:
            continue
        suitable_currency_value, suitable_value = suitable_result
        need_value -= suitable_value
        result_currency_value += suitable_currency_value
        result_value += suitable_value
    if not result_currency_value or not result_value:
        return
    rate_float = result_currency_value / result_value
    find_currency_value = need_value * rate_float
    if find_currency_value > method.currency.div:
        return
    rate = value_to_int(value=rate_float, decimal=method.currency.rate_decimal, round_method=round_method)
    return rate


async def calcs_rate_requisite(method: Method, rate_type: str) -> Optional[int]:
    result = await calcs_requisite(method=method, rate_type=rate_type, value=3_000_00)
    if not result:
        return
    return result
