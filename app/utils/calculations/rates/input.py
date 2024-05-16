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

from app.db.models import Currency, RequisiteTypes, RequisiteStates, OrderTypes, CommissionPackValue
from app.repositories import RequisiteRepository, CommissionPackRepository, CommissionPackValueRepository
from app.utils.calculations.requisite.limits import check_currency_value_limits, check_value_limits
from app.utils.calculations.simples import get_div_by_currency_value, get_div_by_value
from app.utils.calculations.values.comissions import get_commission_value_by_pack


async def get_input_rate_by_currency_value(currency: Currency, currency_value: int) -> Optional[tuple]:
    result_currency_value, result_value = 0, 0
    for requisite in await RequisiteRepository().get_list_input_by_rate(
            type=RequisiteTypes.OUTPUT,
            state=RequisiteStates.ENABLE,
            currency=currency,
            in_process=False,
    ):
        suitable_currency_value = currency_value
        if 0 in [suitable_currency_value, requisite.currency_value, requisite.value]:
            continue
        suitable_currency_value = check_currency_value_limits(
            requisite=requisite,
            currency_value=suitable_currency_value,
        )
        if not suitable_currency_value:
            continue
        suitable_currency_value, suitable_value = get_div_by_currency_value(
            currency_value=suitable_currency_value,
            div=currency.div,
            rate=requisite.rate,
            rate_decimal=currency.rate_decimal,
            type_=OrderTypes.INPUT,
        )
        suitable_value = check_value_limits(
            requisite=requisite,
            value=suitable_value,
        )
        if not suitable_currency_value or not suitable_value:
            continue
        currency_value -= suitable_currency_value
        result_currency_value += suitable_currency_value
        result_value += suitable_value
    if currency_value:
        return
    commission_pack = await CommissionPackRepository().get(is_default=True)
    if not commission_pack:
        return
    commission_pack_value = await CommissionPackValueRepository().get_by_value(
        commission_pack=commission_pack,
        value=result_value,
    )
    result_value += get_commission_value_by_pack(value=result_value, commission_pack_value=commission_pack_value)
    return result_currency_value, result_value, round(result_currency_value / result_value, currency.rate_decimal)


async def get_input_rate_by_value(currency: Currency, value: int) -> Optional[tuple]:
    result_currency_value, result_value = 0, 0
    for requisite in await RequisiteRepository().get_list_input_by_rate(
            type=RequisiteTypes.OUTPUT,
            state=RequisiteStates.ENABLE,
            currency=currency,
            in_process=False,
    ):
        suitable_value = value
        if 0 in [suitable_value, requisite.currency_value, requisite.value]:
            continue
        suitable_value = check_value_limits(
            requisite=requisite,
            value=suitable_value,
        )
        if not suitable_value:
            continue
        suitable_currency_value, suitable_value = get_div_by_value(
            value=suitable_value,
            div=currency.div,
            rate=requisite.rate,
            rate_decimal=currency.rate_decimal,
            type_=OrderTypes.INPUT,
        )
        suitable_currency_value = check_currency_value_limits(
            requisite=requisite,
            currency_value=suitable_currency_value,
        )
        if not suitable_currency_value or not suitable_value:
            continue
        value -= suitable_value
        result_currency_value += suitable_currency_value
        result_value += suitable_value
    if value and value > 100:
        return
    commission_pack = await CommissionPackRepository().get(is_default=True)
    if not commission_pack:
        return
    commission_pack_value = await CommissionPackValueRepository().get_by_value(
        commission_pack=commission_pack,
        value=result_value,
    )
    result_value += get_commission_value_by_pack(value=result_value, commission_pack_value=commission_pack_value)
    return result_currency_value, result_value, round(result_currency_value / result_value, currency.rate_decimal)
