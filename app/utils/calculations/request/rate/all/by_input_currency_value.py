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
from app.utils.calculations.commissions import get_input_commission
from app.utils.schemes.calculations.requests.rate import RequestCalculateScheme
from app.utils.value import value_to_float, value_to_int


async def calculate_request_rate_all_by_input_currency_value(
        input_method: Method,
        output_method: Method,
        commission_pack: CommissionPack,
        input_currency_value: int,
) -> Optional['RequestCalculateScheme']:
    # input rate
    input_rate_db = await RateRepository().get_actual(method=input_method, type=RateTypes.INPUT)
    if not input_rate_db:
        return
    input_rate = input_rate_db.rate
    input_rate_float = value_to_float(value=input_rate, decimal=input_method.currency.rate_decimal)
    # output rate
    output_rate_db = await RateRepository().get_actual(method=output_method, type=RateTypes.OUTPUT)
    if not output_rate_db:
        return
    output_rate = output_rate_db.rate
    output_rate_float = value_to_float(value=output_rate, decimal=output_method.currency.rate_decimal)
    # input values
    input_currency_value_float = value_to_float(value=input_currency_value, decimal=input_method.currency.decimal)
    input_value_float = input_currency_value_float / input_rate_float
    input_value = value_to_int(value=input_value_float)
    # commission
    commission = await get_input_commission(commission_pack=commission_pack, value=input_value)
    commission_float = value_to_float(value=commission)
    # output values
    output_value_float = input_value_float - commission_float
    output_value = value_to_int(value=output_value_float)
    output_currency_value_float = output_value_float * output_rate_float
    output_currency_value = value_to_int(value=output_currency_value_float, decimal=output_method.currency.decimal)
    # calculate rate
    rate_float = output_currency_value_float / input_currency_value_float
    rate_decimal = max([input_method.currency.rate_decimal, output_method.currency.rate_decimal])
    if rate_float < 1:
        rate_decimal *= 2
    rate = value_to_int(value=rate_float, decimal=rate_decimal, round_method=math.floor)

    return RequestCalculateScheme(
        input_currency_value=input_currency_value,
        input_rate=input_rate,
        input_value=input_value,
        commission=commission,
        rate=rate,
        rate_decimal=rate_decimal,
        output_currency_value=output_currency_value,
        output_rate=output_rate,
        output_value=output_value,
    )
