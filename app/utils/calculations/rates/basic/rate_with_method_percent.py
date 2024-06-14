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


from app.db.models import Method, RateTypes
from app.utils.value import value_to_float, value_to_int


async def calculate_rate_with_method_percent(method: Method, rate: int, rate_type: str) -> int:
    rate_float = value_to_float(value=rate, decimal=method.currency.rate_decimal)
    if rate_type == RateTypes.INPUT and method.input_rate_percent:
        percent_float = value_to_float(value=method.input_rate_percent, decimal=method.currency.rate_decimal)
        rate_float = rate_float + rate_float * percent_float
    elif rate_type == RateTypes.OUTPUT and method.output_rate_percent:
        percent_float = value_to_float(value=method.output_rate_percent, decimal=method.currency.rate_decimal)
        rate_float = rate_float - rate_float * percent_float
    return value_to_int(rate_float, decimal=method.currency.rate_decimal)
