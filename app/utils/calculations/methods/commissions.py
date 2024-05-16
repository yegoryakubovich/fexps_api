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

from app.db.models import Method, RateTypes


def get_commission_value_by_method(method: Method, value: int, rate_type: str) -> int:
    result, commission_rate = 0, 10 ** 4
    commission_percent, commission_value = 0, 0
    if rate_type == RateTypes.INPUT:
        commission_percent = method.rate_input_commission_percent
        commission_value = method.rate_input_commission_value
    elif rate_type == RateTypes.OUTPUT:
        commission_percent = method.rate_output_commission_percent
        commission_value = method.rate_output_commission_value
    if commission_percent:
        result += math.ceil(value - value * (commission_rate - commission_percent) / commission_rate)
    if commission_value:
        result += commission_value
    return result
