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


import asyncio
import logging

from app.db.models import Currency, RateTypes, RateSources
from app.repositories import CurrencyRepository, RatePairRepository, RateRepository
from app.tasks.permanents.rates.logger import RateLogger
from app.utils.calculations.rates.bybit import calculate_rate_bybit
from app.utils.calculations.rates.checks import check_actual_rate
from app.utils.calculations.rates.default import calculate_rate_default

custom_logger = RateLogger(prefix='rate_keep_pair')


async def run():
    pairs = []
    for currency_input in await CurrencyRepository().get_list():
        for currency_output in await CurrencyRepository().get_list():
            if currency_input.id_str == currency_output.id_str:
                continue
            pair = (currency_input.id_str, currency_output.id_str)
            if pair in pairs:
                continue
            await update_rate(currency_input=currency_input, currency_output=currency_output)
            pairs.append(pair)
            await asyncio.sleep(0.5)
        await asyncio.sleep(1)
    await asyncio.sleep(60)


async def update_rate(currency_input: Currency, currency_output: Currency):
    rate_decimal = max([currency_input.rate_decimal, currency_output.rate_decimal])
    # INPUT
    rate_value_input = None
    # source our
    rate_input = await RateRepository().get(
        currency=currency_input,
        type=RateTypes.INPUT,
        source=RateSources.OUR,
    )
    if rate_input and await check_actual_rate(rate=rate_input):
        rate_value_input = rate_input.value
    # source default
    if not rate_value_input:
        rate_value_input = await calculate_rate_default(currency=currency_input, rate_type=RateTypes.INPUT)
    # source bybit
    if not rate_value_input:
        rate_input = await RateRepository().get(
            currency=currency_input,
            type=RateTypes.INPUT,
            source=RateSources.BYBIT,
        )
        if rate_input and await check_actual_rate(rate=rate_input):
            rate_value_input = await calculate_rate_bybit(rate=rate_input)
    # source other
    if not rate_value_input:
        rate_input = await RateRepository().get(
            currency=currency_input,
            type=RateTypes.INPUT,
        )
        if rate_input and await check_actual_rate(rate=rate_input):
            rate_value_input = rate_input.value
    # finish check
    if rate_value_input is None:
        logging.critical(f'{currency_input.id_str}{currency_output.id_str} input not found')
        return
    # OUTPUT
    rate_value_output = None
    # source our
    rate_output = await RateRepository().get(
        currency=currency_output,
        type=RateTypes.OUTPUT,
        source=RateSources.OUR,
    )
    if rate_output and await check_actual_rate(rate=rate_output):
        rate_value_output = rate_output.value
    # source default
    if not rate_value_output:
        rate_value_output = await calculate_rate_default(currency=currency_output, rate_type=RateTypes.OUTPUT)
    # source bybit
    if not rate_value_output:
        rate_output = await RateRepository().get(
            currency=currency_output,
            type=RateTypes.OUTPUT,
            source=RateSources.BYBIT,
        )
        if rate_output and await check_actual_rate(rate=rate_output):
            rate_value_output = await calculate_rate_bybit(rate=rate_output)
    # source other
    if not rate_value_output:
        rate_output = await RateRepository().get(
            currency=currency_output,
            type=RateTypes.OUTPUT,
        )
        if rate_output and await check_actual_rate(rate=rate_output):
            rate_value_output = rate_output.value
    # finish check
    if rate_value_output is None:
        logging.critical(f'{currency_input.id_str}{currency_output.id_str} output not found')
        return
    # result
    rate_input_value = rate_value_input * 10 ** (rate_decimal - currency_input.rate_decimal)
    rate_output_value = rate_value_output * 10 ** (rate_decimal - currency_output.rate_decimal)
    rate_value = round(rate_input_value / rate_output_value * 10 ** rate_decimal)
    logging.critical(
        f'{currency_input.id_str}{currency_output.id_str}: '
        f'rate_input_value {rate_input_value} | '
        f'rate_output_value {rate_output_value} | '
        f'rate_value {rate_value}'
    )
    if not rate_value:
        return
    await RatePairRepository().create(
        currency_input=currency_input,
        currency_output=currency_output,
        rate_decimal=rate_decimal,
        value=rate_value,
    )


async def rate_keep_pair_our():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
