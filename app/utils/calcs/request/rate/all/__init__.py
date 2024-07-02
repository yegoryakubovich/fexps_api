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
from app.utils.schemes.calcs.requests.rate import RequestCalculateScheme
from .by_input_currency_value import calcs_request_rate_all_by_input_currency_value
from .by_output_currency_value import calcs_request_rate_all_by_output_currency_value


async def calcs_request_rate_all(
        input_method: Method,
        output_method: Method,
        commission_pack: CommissionPack,
        input_currency_value: Optional[int] = None,
        output_currency_value: Optional[int] = None,
) -> Optional['RequestCalculateScheme']:
    if input_currency_value:
        return await calcs_request_rate_all_by_input_currency_value(
            input_method=input_method,
            output_method=output_method,
            commission_pack=commission_pack,
            input_currency_value=input_currency_value,
        )
    elif output_currency_value:
        return await calcs_request_rate_all_by_output_currency_value(
            input_method=input_method,
            output_method=output_method,
            commission_pack=commission_pack,
            output_currency_value=output_currency_value,
        )
