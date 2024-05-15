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


from typing import Optional

from app.db.models import Currency
from app.utils.calculations.rates.input import get_input_rate_by_currency_value, get_input_rate_by_value
from app.utils.calculations.rates.output import get_output_rate_by_value


async def get_all_rate_by_currency_value(
        input_currency: Currency,
        output_currency: Currency,
        currency_value: int,
) -> Optional[tuple]:
    rate_decimal = max([input_currency.rate_decimal, output_currency.rate_decimal])
    input_result = await get_input_rate_by_currency_value(currency=input_currency, currency_value=currency_value)
    if not input_result:
        return
    output_result = await get_output_rate_by_value(currency=output_currency, value=input_result[1])
    if not output_result:
        return
    return input_result[0], output_result[0], round(input_result[0] / output_result[0], rate_decimal)


async def get_all_rate_by_value(
        input_currency: Currency,
        output_currency: Currency,
        value: int,
) -> Optional[tuple]:
    rate_decimal = max([input_currency.rate_decimal, output_currency.rate_decimal])
    input_result = await get_input_rate_by_value(currency=input_currency, value=value)
    if not input_result:
        return
    output_result = await get_output_rate_by_value(currency=output_currency, currency_value=input_result[1])
    if not output_result:
        return
    return input_result[0], output_result[0], round(input_result[0] / output_result[0], rate_decimal)
