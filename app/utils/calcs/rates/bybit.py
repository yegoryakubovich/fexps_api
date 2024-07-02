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

from app.db.models import RateSources, Method
from app.repositories import RateParseRepository
from app.utils.calcs.rates.basic.rate_with_method_percent import calcs_rate_with_method_percent


async def calcs_rate_bybit(method: Method, rate_type: str) -> Optional[int]:
    rate_parse = await RateParseRepository().get(currency=method.currency, source=RateSources.BYBIT, type=rate_type)
    if not rate_parse:
        return
    rate = rate_parse.rate
    rate = await calcs_rate_with_method_percent(method=method, rate=rate, rate_type=rate_type)
    return rate
