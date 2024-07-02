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

from app.db.models import CommissionPack
from app.repositories import CommissionPackValueRepository
from app.utils.value import value_to_float, value_to_int


async def get_input_commission(commission_pack: CommissionPack, value: int) -> int:
    commission_pack_value = await CommissionPackValueRepository().get_by_value(
        commission_pack=commission_pack,
        value=value,
    )
    value_float = value_to_float(value=value)
    commission_value_float = value_to_float(value=commission_pack_value.value)
    commission_percent_float = value_to_float(value=commission_pack_value.percent)
    commission_float = commission_value_float + (value_float - commission_value_float) * commission_percent_float / 100
    return value_to_int(value=commission_float, round_method=math.ceil)
