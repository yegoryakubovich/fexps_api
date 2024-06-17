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

from app.db.models import Method, CommissionPack
from app.utils.schemes.calculations.requests.rate import RequestCalculateScheme


async def calculate_request_rate_input(
        input_method: Method,
        commission_pack: CommissionPack,
        input_currency_value: Optional[int] = None,
        input_value: Optional[int] = None,
) -> Optional['RequestCalculateScheme']:
    if input_currency_value:
        return
    elif input_value:
        return
