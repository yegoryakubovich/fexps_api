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

from app.db.models import Currency
from .input import calc_input_value2currency, calc_input_currency2value
from .output import calc_output_value2currency, calc_output_currency2value


async def calc_all(
        currency_input: Currency,
        currency_output: Currency,
        currency_value_input: float = None,
        currency_value_output: float = None,
) -> dict:
    if currency_value_input:
        calc_input = await calc_input_currency2value(currency=currency_input, currency_value=currency_value_input)
        calc_output = await calc_output_value2currency(currency=currency_output, value=calc_input['value'])
        rate_fix = math.ceil(calc_input['currency_value'] / calc_output['currency_value'] * 100)
        return {
            'calc_input': calc_input,
            'calc_output': calc_output,
            'currency_value_input': calc_input['currency_value'],
            'currency_value_output': calc_output['currency_value'],
            'rate': rate_fix,
        }
    elif currency_value_output:
        calc_output = await calc_output_currency2value(currency=currency_output, currency_value=currency_value_output)
        calc_input = await calc_input_value2currency(currency=currency_input, value=calc_output['value'])
        rate_fix = math.ceil(calc_input['currency_value'] / calc_output['currency_value'] * 100)
        return {
            'calc_output': calc_input,
            'calc_input': calc_output,
            'currency_value_input': calc_input['currency_value'],
            'currency_value_output': calc_output['currency_value'],
            'rate': rate_fix,
        }
