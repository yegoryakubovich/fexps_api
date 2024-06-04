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

from app.db.models import RateTypes, RateSources, Method
from app.repositories import RateRepository
from app.utils.calculations.rates.bybit import calculate_rate_bybit
from app.utils.calculations.rates.checks import check_actual_rate
from app.utils.calculations.rates.default import calculate_rate_default
from app.utils.calculations.schemes.loading import TypesScheme


async def calc_request_full_output(
        output_method: Method,
        rate_decimal: int,
        currency_value=None,
        value=None,
) -> Optional[TypesScheme]:
    currency = output_method.currency
    request_rate = None
    # source our
    rate = await RateRepository().get(
        currency=currency,
        type=RateTypes.INPUT,
        source=RateSources.OUR,
    )
    if rate and await check_actual_rate(rate=rate):
        request_rate = rate.value
    # source default
    if not request_rate:
        default_result = await calculate_rate_default(currency=currency, rate_type=RateTypes.INPUT)
        request_rate = default_result.rate
    # source bybit
    if not request_rate:
        rate = await RateRepository().get(
            currency=currency,
            type=RateTypes.INPUT,
            source=RateSources.BYBIT,
        )
        if rate and await check_actual_rate(rate=rate):
            bybit_result = await calculate_rate_bybit(rate=rate)
            request_rate = bybit_result.rate
    # source other
    if not request_rate:
        rate = await RateRepository().get(
            currency=currency,
            type=RateTypes.INPUT,
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
    return TypesScheme(currency_value=currency_value, value=value, commission_value=0)
