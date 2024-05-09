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

from app.db.models import Request, RequestTypes, RequestFirstLine


def get_rate_by_input(
        currency_value: int,
        value: int,
        rate_decimal: int,
) -> int:
    return math.ceil(currency_value / value * (10 ** rate_decimal))


def get_rate_by_output(
        currency_value: int,
        value: int,
        rate_decimal: int,
) -> int:
    return math.floor(currency_value / value * (10 ** rate_decimal))


def get_auto_rate(
        request: Request,
        currency_value: int,
        value: int,
) -> int:
    if request.type == RequestTypes.ALL and request.first_line in RequestFirstLine.choices_output:
        return get_rate_by_input(
            currency_value=currency_value,
            value=value,
            rate_decimal=request.rate_decimal,
        )
    return get_rate_by_input(
        currency_value=currency_value,
        value=value,
        rate_decimal=request.rate_decimal,
    )
