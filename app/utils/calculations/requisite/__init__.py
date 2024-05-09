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

from app.db.models import RequisiteTypes


async def all_value_calc(
        type_: [RequisiteTypes, str],
        rate_decimal: int,
        currency_value: int,
        value: int,
        rate: int,
) -> tuple[int, int, int]:
    rate_currency_value_method = math.ceil if type_ == RequisiteTypes.OUTPUT else math.floor
    value_method = math.floor if type_ == RequisiteTypes.OUTPUT else math.ceil
    if currency_value and value:
        rate = rate_currency_value_method(currency_value / value * 10 ** rate_decimal)
    elif currency_value and rate:
        value = value_method(currency_value / rate * 10 ** rate_decimal)
    else:
        currency_value = rate_currency_value_method(value * rate / 10 ** rate_decimal)
    return currency_value, value, rate
