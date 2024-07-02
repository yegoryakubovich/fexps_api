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

from app.db.models import Method, RateTypes
from app.repositories import RateRepository
from app.utils.schemes.calcs.requests.rate import RequestCalculateScheme
from app.utils.value import value_to_float, value_to_int


async def calcs_request_rate_output_by_output_value(
        output_method: Method,
        output_value: int,
) -> Optional['RequestCalculateScheme']:
    # output rate
    output_rate_db = await RateRepository().get_actual(method=output_method, type=RateTypes.OUTPUT)
    if not output_rate_db:
        return
    output_rate = output_rate_db.rate
    output_rate_float = value_to_float(value=output_rate, decimal=output_method.currency.rate_decimal)
    # output values
    output_value_float = value_to_float(value=output_value)
    output_currency_value_float = output_value_float * output_rate_float
    output_currency_value = value_to_int(value=output_currency_value_float, decimal=output_method.currency.decimal)
    output_currency_value_temp = output_currency_value
    output_currency_value = math.floor(output_currency_value / output_method.currency.div) * output_method.currency.div
    difference = math.floor((output_currency_value_temp - output_currency_value) / output_rate_float)
    # calculate rate
    rate_float = output_currency_value / output_value
    rate_decimal = max([output_method.currency.rate_decimal])
    if rate_float < 1:
        rate_decimal *= 2
    rate = value_to_int(value=rate_float, decimal=rate_decimal, round_method=math.floor)

    return RequestCalculateScheme(
        input_currency_value=None,
        input_rate=None,
        input_value=None,
        difference=0,
        commission=0,
        rate=rate,
        rate_decimal=rate_decimal,
        output_currency_value=output_currency_value,
        output_rate=output_rate * 10 ** (rate_decimal - output_method.currency.rate_decimal),
        output_value=output_value,
    )
