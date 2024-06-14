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

from app.db.models import Method, RateTypes
from app.utils.calculations.rates.basic import calculate_rate_with_method_percent


async def calculate_rate_default(method: Method, rate_type: str) -> Optional[int]:
    rate = None
    if rate_type == RateTypes.INPUT and method.input_rate_default:
        rate = method.input_rate_default
    elif rate_type == RateTypes.OUTPUT and method.output_rate_default:
        rate = method.output_rate_default
    if not rate:
        return
    rate = await calculate_rate_with_method_percent(method=method, rate=rate, rate_type=rate_type)
    return rate
