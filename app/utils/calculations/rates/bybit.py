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

from pydantic import BaseModel

from app.db.models import RateTypes, Rate
from app.repositories import MethodRepository, CommissionPackRepository
from app.utils.calculations.values.comissions import get_commission_value_by_pack


class ResultScheme(BaseModel):
    value: int
    rate: int
    commission_value: int
    rate_decimal: int


async def calculate_rate_bybit(
        rate: Rate,
        value: int = 1000_00,
) -> Optional[ResultScheme]:
    result_rate = rate.value
    result_value = value
    currency = rate.currency
    method = await MethodRepository().get(currency=currency, is_rate_default=True)
    if rate.type == RateTypes.INPUT:
        commission_pack = await CommissionPackRepository().get(is_default=True)
        if not commission_pack:
            return
        commission_value = await get_commission_value_by_pack(value=value, commission_pack=commission_pack)
        result_value += commission_value
        if method and method.rate_input_percent or True:
            result_rate_float = result_rate / 10 ** currency.rate_decimal
            rate_input_percent_float = method.rate_input_percent / 10 ** currency.rate_decimal
            result_rate_float = result_rate_float / (1 - rate_input_percent_float)
            result_rate = result_rate_float * 10 ** currency.rate_decimal
        round_func = math.ceil
    else:
        commission_value = 0
        if method and method.rate_output_percent or True:
            result_rate_float = result_rate / 10 ** currency.rate_decimal
            rate_output_percent_float = method.rate_output_percent / 10 ** currency.rate_decimal
            result_rate_float = result_rate_float * (1 - rate_output_percent_float)
            result_rate = result_rate_float * 10 ** currency.rate_decimal
        round_func = math.floor
    result_value = result_value / result_rate * 10 ** currency.rate_decimal
    result_rate = round_func(value / result_value * 10 ** currency.rate_decimal)
    return ResultScheme(
        value=value,
        rate=result_rate,
        commission_value=commission_value,
        rate_decimal=currency.rate_decimal,
    )
