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
from typing import Optional

from app.db.models import RateTypes, RateSources, RequestFirstLine, Method
from app.repositories import RateRepository, WalletRepository, CommissionPackValueRepository
from app.utils.calculations.rates.bybit import calculate_rate_bybit
from app.utils.calculations.rates.checks import check_actual_rate
from app.utils.calculations.rates.default import calculate_rate_default
from app.utils.calculations.request.commissions import get_commission_value_input, \
    get_commission_value_output
from app.utils.calculations.schemes.loading import TypesScheme


async def get_commission(
        first_line: str,
        wallet_id: int,
        value: int,
) -> int:
    wallet = await WalletRepository().get_by_id(id_=wallet_id)
    commission_pack_value = await CommissionPackValueRepository().get_by_value(
        commission_pack=wallet.commission_pack,
        value=value,
    )
    if first_line in RequestFirstLine.choices_input:
        return get_commission_value_input(value=value, commission_pack_value=commission_pack_value)
    elif first_line in RequestFirstLine.choices_output:
        return get_commission_value_output(value=value, commission_pack_value=commission_pack_value)


async def calc_request_full_input(
        first_line: str,
        input_method: Method,
        rate_decimal: int,
        wallet_id: int,
        currency_value=None,
        value=None,
) -> Optional[TypesScheme]:
    currency = input_method.currency
    request_rate = None
    rate = await RateRepository().get(
        currency=currency,
        type=RateTypes.OUTPUT,
        source=RateSources.OUR,
    )
    if rate and await check_actual_rate(rate=rate):
        request_rate = rate.value
    # source default
    if not request_rate:
        default_result = await calculate_rate_default(currency=currency, rate_type=RateTypes.OUTPUT)
        if default_result:
            request_rate = default_result.rate
    # source bybit
    if not request_rate:
        rate = await RateRepository().get(
            currency=currency,
            type=RateTypes.OUTPUT,
            source=RateSources.BYBIT,
        )
        if rate and await check_actual_rate(rate=rate):
            bybit_result = await calculate_rate_bybit(rate=rate)
            if bybit_result:
                request_rate = bybit_result.rate
    # source other
    if not request_rate:
        rate = await RateRepository().get(
            currency=currency,
            type=RateTypes.OUTPUT,
        )
        if rate and await check_actual_rate(rate=rate):
            request_rate = rate.value
    # finish check
    if request_rate is None:
        return
    if currency.rate_decimal != rate_decimal:
        request_rate *= 10 ** (rate_decimal - currency.rate_decimal)
    if currency_value:
        value = round(currency_value / (request_rate / 10 ** rate_decimal))
    elif value:
        currency_value = value * (request_rate / 10 ** rate_decimal) // currency.div * currency.div
    if None in [currency_value, value]:
        return
    commission_value = await get_commission(
        first_line=first_line,
        wallet_id=wallet_id,
        value=value,
    )
    return TypesScheme(currency_value=currency_value, value=value, commission_value=commission_value)
