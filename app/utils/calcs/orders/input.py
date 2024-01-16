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

from app.db.models import Currency, RequisiteTypes
from app.repositories.requisite import RequisiteRepository
from app.utils.custom_calc import minus, round_floor, round_ceil


async def calc_input_currency2value(
        currency: Currency,
        currency_value: float,
) -> dict:
    selected_requisites = []
    for requisite in await RequisiteRepository().get_list_input_by_rate(
            type=RequisiteTypes.INPUT, currency=currency,
    ):
        if 0 in [currency_value, requisite.currency_value]:
            continue
        if requisite.currency_value >= currency_value:
            suitable_currency_value = currency_value
        else:
            suitable_currency_value = requisite.currency_value
        suitable_value = math.floor(suitable_currency_value / requisite.rate)
        selected_requisites.append({
            'requisite_id': requisite.id,
            'currency_value': suitable_currency_value,
            'value': suitable_value,
            'rate': requisite.rate,
        })
        currency_value = round(currency_value - suitable_currency_value)
    currency_value_fix = 0
    value_fix = 0
    for select_requisite in selected_requisites:
        currency_value_fix += select_requisite.get('currency_value')
        value_fix += select_requisite.get('value')
    rate_fix = round_ceil(currency_value_fix / value_fix)
    return {
        'selected_requisites': selected_requisites,
        'currency_value': currency_value_fix,
        'value': value_fix,
        'rate_fix': rate_fix,
    }


async def calc_input_value2currency(
        currency: Currency,
        value: float,
) -> dict:
    selected_requisites = []
    for requisite in await RequisiteRepository().get_list_input_by_rate(
            type=RequisiteTypes.INPUT, currency=currency,
    ):
        if 0 in [value, requisite.value]:
            continue
        if requisite.value >= value:
            suitable_value = value
        else:
            suitable_value = requisite.value
        suitable_currency_value = math.ceil(suitable_value * requisite.rate)
        selected_requisites.append({
            'requisite_id': requisite.id,
            'currency_value': suitable_currency_value,
            'value': suitable_value,
            'rate': requisite.rate,
        })
        value = round(value - suitable_value)
    currency_value_fix = 0
    value_fix = 0
    for select_requisite in selected_requisites:
        currency_value_fix += select_requisite.get('currency_value')
        value_fix += select_requisite.get('value')
    rate_fix = round_ceil(currency_value_fix / value_fix)
    return {
        'selected_requisites': selected_requisites,
        'currency_value': currency_value_fix,
        'value': value_fix,
        'rate_fix': rate_fix,
    }


async def calc_input(
        currency: Currency,
        value: float = None,
        currency_value: float = None,
) -> dict:
    if currency_value:
        return await calc_input_currency2value(currency=currency, currency_value=currency_value)
    elif value:
        return await calc_input_value2currency(currency=currency, value=value)
