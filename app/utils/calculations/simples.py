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

from app.db.models import OrderTypes


def get_div_by_currency_value(
        currency_value: int, div: int, rate: int, rate_decimal: int, order_type: str,
) -> tuple[int, int]:
    currency_value = round(currency_value // div * div)
    if order_type == OrderTypes.INPUT:
        value = math.floor(currency_value / rate * 10 ** rate_decimal)
    else:
        value = math.ceil(currency_value / rate * 10 ** rate_decimal)
    return currency_value, value


def get_div_by_value(
        value: int, div: int, rate: int, rate_decimal: int, type_: str,
) -> tuple[int, int]:
    currency_value = round(value * rate / 10 ** rate_decimal)
    currency_value = round(currency_value // div * div)
    if type_ == OrderTypes.INPUT:
        value = math.floor(currency_value / rate * 10 ** rate_decimal)
    else:
        value = math.ceil(currency_value / rate * 10 ** rate_decimal)
    return currency_value, value
