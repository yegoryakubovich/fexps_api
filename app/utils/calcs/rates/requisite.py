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
from app.utils.calcs.requisites.find.input_by_value import calcs_requisite_input_by_value
from app.utils.calcs.requisites.find.output_by_value import calcs_requisite_output_by_value


async def calcs_rate_requisite(method: Method, rate_type: str) -> Optional[int]:
    result = None
    if rate_type == RateTypes.INPUT:
        result = await calcs_requisite_input_by_value(method=method, value=3_000_00)
    elif rate_type == RateTypes.OUTPUT:
        result = await calcs_requisite_output_by_value(method=method, value=3_000_00)
    if not result:
        return
    return result.rate
