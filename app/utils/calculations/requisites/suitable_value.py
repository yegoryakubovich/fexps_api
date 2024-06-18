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

from app.db.models import Requisite, RateTypes
from app.utils.value import value_to_float


async def calculate_requisite_suitable_from_value(
        requisite: Requisite,
        need_value: int,
) -> Optional[tuple[int, int]]:
    value = need_value
    if requisite.value_min and value < requisite.value_min:
        return
    if value > requisite.value:
        value = requisite.value
    if requisite.value_max and value > requisite.value_max:
        value = requisite.value_max
    rate_float = value_to_float(value=requisite.rate, decimal=requisite.currency.rate_decimal)
    currency_value = value * rate_float // requisite.currency.div * requisite.currency.div
    if requisite.type == RateTypes.INPUT:
        value = math.ceil(currency_value / rate_float)
    elif requisite.type == RateTypes.OUTPUT:
        value = math.floor(currency_value / rate_float)
    if not value or not currency_value:
        return
    return currency_value, value


async def calculate_requisite_suitable_from_currency_value(
        requisite: Requisite,
        need_currency_value: int,
) -> Optional[tuple[int, int]]:
    currency_value = need_currency_value
    value = None
    if currency_value < requisite.currency.div:
        return
    if requisite.currency_value_min and currency_value < requisite.currency_value_min:
        return
    if currency_value > requisite.currency_value:
        currency_value = requisite.currency_value
    if requisite.currency_value_max and currency_value > requisite.currency_value_max:
        currency_value = requisite.currency_value_max
    rate_float = value_to_float(value=requisite.rate, decimal=requisite.currency.rate_decimal)
    currency_value = currency_value // requisite.currency.div * requisite.currency.div
    if requisite.type == RateTypes.INPUT:
        value = math.ceil(currency_value / rate_float)
    elif requisite.type == RateTypes.OUTPUT:
        value = math.floor(currency_value / rate_float)
    if not value or not currency_value:
        return
    return currency_value, value
