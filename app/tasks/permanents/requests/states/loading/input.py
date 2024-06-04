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

from app.db.models import Request, RateTypes, RateSources
from app.repositories import RateRepository
from app.tasks.permanents.requests.logger import RequestLogger
from app.utils.calculations.rates.bybit import calculate_rate_bybit
from app.utils.calculations.rates.checks import check_actual_rate
from app.utils.calculations.rates.default import calculate_rate_default
from app.utils.calculations.request.commissions import get_commission
from app.utils.calculations.schemes.loading import TypesScheme

custom_logger = RequestLogger(prefix='request_state_loading_input_check')


async def request_type_input(
        request: Request,
        currency_value=None,
        value=None,
) -> Optional[TypesScheme]:
    currency = request.input_method.currency
    request_rate = None
    commission_value = None
    rate = await RateRepository().get(
        currency=currency,
        type=RateTypes.OUTPUT,
        source=RateSources.OUR,
    )
    if rate and await check_actual_rate(rate=rate):
        request_rate = rate.value
        if request_rate:
            commission_value = await get_commission(request=request, wallet_id=request.wallet_id, value=value)
    logging.critical(f'our - {request_rate}')
    logging.critical(f'our - {commission_value}')
    # source default
    if not request_rate:
        default_result = await calculate_rate_default(currency=currency, rate_type=RateTypes.OUTPUT)
        if default_result:
            request_rate = default_result.rate
            commission_value = default_result.commission_value
    logging.critical(f'default - {request_rate}')
    logging.critical(f'default - {commission_value}')
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
                commission_value = bybit_result.commission_value
    logging.critical(f'bybit - {request_rate}')
    logging.critical(f'bybit - {commission_value}')
    # source other
    if not request_rate:
        rate = await RateRepository().get(
            currency=currency,
            type=RateTypes.OUTPUT,
        )
        if rate and await check_actual_rate(rate=rate):
            request_rate = rate.value
            if request_rate:
                commission_value = await get_commission(request=request, wallet_id=request.wallet_id, value=value)
    logging.critical(f'other - {request_rate}')
    logging.critical(f'other - {commission_value}')
    # finish check
    if request_rate is None:
        custom_logger.critical(text=f'{currency.id_str}input not found')
        return
    if currency.rate_decimal != request.rate_decimal:
        request_rate *= 10 ** (request.rate_decimal - currency.rate_decimal)
    if currency_value:
        value = round(currency_value / (request_rate / 10 ** request.rate_decimal))
    elif value:
        currency_value = value * (request_rate / 10 ** request.rate_decimal) // currency.div * currency.div
    if None in [currency_value, value]:
        return
    logging.critical(f'request_rate={request_rate}')
    return TypesScheme(currency_value=currency_value, value=value, commission_value=commission_value)
