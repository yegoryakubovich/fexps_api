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


import logging
import math

from app.db.models import CommissionPackValue, RequestFirstLine, Request
from app.repositories.commission_pack_value import CommissionPackValueRepository
from app.repositories.wallet import WalletRepository
from app.utils.exceptions.commission_pack import IntervalNotExistsError


def get_commission_value_input(
        value: int,
        commission_pack_value: CommissionPackValue,
) -> int:
    result = 0
    commission_rate = 10 ** 4
    if commission_pack_value.percent:
        result += math.ceil(value - value * (commission_rate - commission_pack_value.percent) / commission_rate)
    if commission_pack_value.value:
        result += commission_pack_value.value
    return result


def get_commission_value_output(
        value: int,
        commission_pack_value: CommissionPackValue,
) -> int:
    result = 0
    commission_rate = 10 ** 4
    if commission_pack_value.value:
        result += commission_pack_value.value
        value = round(value + commission_pack_value.value)
    if commission_pack_value.percent:
        result += math.ceil(value / (commission_rate - commission_pack_value.percent) * commission_rate - value)
    return result


async def get_commission(
        request: Request,
        wallet_id: int,
        value: int,
) -> int:
    wallet = await WalletRepository().get_by_id(id_=wallet_id)
    commission_pack_value = await CommissionPackValueRepository().get_by_value(
        commission_pack=wallet.commission_pack,
        value=value,
    )
    if not commission_pack_value:
        raise IntervalNotExistsError(
            kwargs={
                'value': value,
            },
        )
    if request.first_line in RequestFirstLine.choices_input:
        return get_commission_value_input(value=value, commission_pack_value=commission_pack_value)
    elif request.first_line in RequestFirstLine.choices_output:
        return get_commission_value_output(value=value, commission_pack_value=commission_pack_value)
    logging.error(f'[get_commission] first_line error ({request.first_line})')
