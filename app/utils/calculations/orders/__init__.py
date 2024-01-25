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

from app.db.models import Currency
from app.utils.schemes.calculations.orders import CalcAllOrderScheme
from .input import calc_input_value_to_currency, calc_input_currency_to_value
from .output import calc_output_currency_to_value, calc_output_value_to_currency


async def calc_all(
        currency_input: Currency,
        currency_output: Currency,
        currency_value_input: float = None,
        currency_value_output: float = None,
) -> 'CalcAllOrderScheme':
    if currency_value_input:
        input_calc = await calc_input_currency_to_value(
            currency=currency_input, currency_value=currency_value_input,
        )
        output_calc = await calc_output_value_to_currency(
            currency=currency_output, value=input_calc.value,
        )
        rate_result = math.ceil(input_calc.currency_value / output_calc.currency_value * 100)
        return CalcAllOrderScheme(
            input_calc=input_calc, output_calc=output_calc,
            input_currency_value=input_calc.currency_value, output_currency_value=output_calc.currency_value,
            rate=rate_result,
        )
    elif currency_value_output:
        output_calc = await calc_output_currency_to_value(
            currency=currency_output, currency_value=currency_value_output,
        )
        input_calc = await calc_input_value_to_currency(
            currency=currency_input, value=output_calc.value,
        )
        rate_result = math.ceil(input_calc.currency_value / output_calc.currency_value * 100)
        return CalcAllOrderScheme(
            input_calc=input_calc, output_calc=output_calc,
            input_currency_value=input_calc.currency_value, output_currency_value=output_calc.currency_value,
            rate=rate_result,
        )
