#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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
from typing import List

from app.repositories.commission_pack import CommissionRepository, IntervalNotFoundError
from app.repositories.commission_pack_value import CommissionWalletRepository
from app.repositories.wallet import WalletRepository
from app.utils.schemes.calculations.orders import CalcRequisiteScheme


def get_results_by_calc_requisites(
        calc_requisites: List[CalcRequisiteScheme],
        type_: str,
) -> tuple[int, int, int]:
    currency_value_result, value_result = 0, 0
    for calc_requisite in calc_requisites:
        currency_value_result = round(currency_value_result + calc_requisite.currency_value)
        value_result = round(value_result + calc_requisite.value)
    if type_ == 'input':
        rate_result = math.ceil(currency_value_result / value_result * 100)
    else:
        rate_result = math.floor(currency_value_result / value_result * 100)
    return currency_value_result, value_result, rate_result


def get_commission_by_percent(value: int, commission_percent: int) -> int:
    return round(value * commission_percent / 10000)


async def get_commission(wallet_id: int, value: int) -> int:
    wallet = await WalletRepository().get_by_id(id_=wallet_id)
    commission_wallet = await CommissionWalletRepository().get(wallet=wallet)
    if commission_wallet:
        if commission_wallet.percent:
            return get_commission_by_percent(value=value, commission_percent=commission_wallet.percent)
        elif commission_wallet.value:
            return commission_wallet.value

    commission = await CommissionRepository().get_by_value(value=value)
    if not commission:
        raise IntervalNotFoundError(f'By value == "{value}" not found suitable interval')
    if commission.percent:
        return get_commission_by_percent(value=value, commission_percent=commission.percent)
    elif commission.value:
        return commission.value
