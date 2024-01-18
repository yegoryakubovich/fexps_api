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


from app.db.models import Currency
from app.utils.schemes.calculations.orders import CalcOrderScheme
from .currency_to_value import calc_input_currency_to_value
from .value_to_currency import calc_input_value_to_currency


async def calc_input(
        currency: Currency,
        value: int = None,
        currency_value: int = None,
) -> 'CalcOrderScheme':
    if currency_value:
        return await calc_input_currency_to_value(currency=currency, currency_value=currency_value)
    elif value:
        return await calc_input_value_to_currency(currency=currency, value=value)
