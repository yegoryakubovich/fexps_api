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
from app.utils.calcs.commissions import get_input_commission
from app.utils.schemes.calcs.requests.rate import RequestCalculateScheme
from app.utils.value import value_to_float, value_to_int


async def calcs_request_rate_input_by_input_currency_value(
        input_method: Method,
        commission_pack: CommissionPack,
        input_currency_value: int,
) -> Optional['RequestCalculateScheme']:
    # input rate
    input_rate_db = await RateRepository().get_actual(method=input_method, type=RateTypes.INPUT)
    if not input_rate_db:
        return
    input_rate = input_rate_db.rate
    input_rate_float = value_to_float(value=input_rate, decimal=input_method.currency.rate_decimal)
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
    # calculate rate
    rate_float = output_value / input_currency_value
    rate_decimal = max([input_method.currency.rate_decimal])
    if rate_float < 1:
        rate_decimal *= 2
    rate = value_to_int(value=rate_float, decimal=rate_decimal, round_method=math.floor)

    return RequestCalculateScheme(
        input_currency_value=input_currency_value,
        input_rate=input_rate * 10 ** (rate_decimal - input_method.currency.rate_decimal),
        input_value=input_value,
        difference=0,
        commission=commission,
        rate=rate,
        rate_decimal=rate_decimal,
        output_currency_value=None,
        output_rate=None,
        output_value=None,
    )
