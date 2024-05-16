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
from typing import Optional

from app.db.models import CommissionPackValue, Wallet
from app.repositories import CommissionPackValueRepository, WalletRepository


def get_commission_value_by_pack(commission_pack_value: CommissionPackValue, value: int) -> int:
    result = 0
    commission_rate = 10 ** 4
    if commission_pack_value.percent:
        result += math.ceil(value - value * (commission_rate - commission_pack_value.percent) / commission_rate)
    if commission_pack_value.value:
        result += commission_pack_value.value
    return result


async def get_commission_value_by_wallet(wallet: Wallet, value: int) -> Optional[int]:
    commission_pack = await WalletRepository().get_commission_pack(wallet=wallet)
    if not commission_pack:
        return
    commission_pack_value = await CommissionPackValueRepository().get_by_value(
        commission_pack=commission_pack,
        value=value,
    )
    return get_commission_value_by_pack(commission_pack_value=commission_pack_value, value=value)
