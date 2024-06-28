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

from app.db.models import Method, RateTypes, CommissionPack
from app.repositories import RateRepository
from app.utils.calculations.commissions import get_output_commission
from app.utils.schemes.calculations.requests.rate import RequestCalculateScheme
from app.utils.value import value_to_float, value_to_int


async def calculate_request_rate_all_by_output_currency_value(
        input_method: Method,
        output_method: Method,
        commission_pack: CommissionPack,
        output_currency_value: int,
) -> Optional['RequestCalculateScheme']:
    # output rate
    output_rate_db = await RateRepository().get_actual(method=output_method, type=RateTypes.OUTPUT)
    if not output_rate_db:
        return
    output_rate = output_rate_db.rate
    output_rate_float = value_to_float(value=output_rate, decimal=output_method.currency.rate_decimal)
    # input rate
    input_rate_db = await RateRepository().get_actual(method=input_method, type=RateTypes.INPUT)
    if not input_rate_db:
        return
    input_rate = input_rate_db.rate
    input_rate_float = value_to_float(value=input_rate, decimal=input_method.currency.rate_decimal)
    # output values
    output_currency_value_float = value_to_float(
        value=output_currency_value,
        decimal=output_method.currency.decimal,
    )
    output_value_float = output_currency_value_float / output_rate_float
    output_value = value_to_int(value=output_value_float)
    # commission
    commission = await get_output_commission(commission_pack=commission_pack, value=output_value)
    commission_float = value_to_float(value=commission)
    # input values
    input_value_float = output_value_float + commission_float
    input_value = value_to_int(value=input_value_float)
    input_currency_value_float = input_value_float * input_rate_float
    input_currency_value = value_to_int(value=input_currency_value_float, decimal=input_method.currency.decimal)
    input_currency_value_temp = input_currency_value
    input_currency_value = math.ceil(input_currency_value / input_method.currency.div) * input_method.currency.div
    difference = math.floor((input_currency_value - input_currency_value_temp) / input_rate_float)
    # calculate rate
    rate_float = output_currency_value / input_currency_value
    rate_decimal = max([input_method.currency.rate_decimal, output_method.currency.rate_decimal])
    if rate_float < 1:
        rate_decimal *= 2
    rate = value_to_int(value=rate_float, decimal=rate_decimal, round_method=math.ceil)

    return RequestCalculateScheme(
        input_currency_value=input_currency_value,
        input_rate=input_rate * 10 ** (rate_decimal - input_method.currency.rate_decimal),
        input_value=input_value,
        difference=difference,
        commission=commission,
        rate=rate,
        rate_decimal=rate_decimal,
        output_currency_value=output_currency_value,
        output_rate=output_rate * 10 ** (rate_decimal - output_method.currency.rate_decimal),
        output_value=output_value,
    )
