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
import datetime
import logging

from app.db.models import Currency, RateTypes, RateSources, Rate
from app.repositories import CurrencyRepository, RatePairRepository, RateRepository
from app.tasks.permanents.rates.logger import RateLogger
from app.utils.calculations.rates.default import rate_get_default
from config import settings

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
    if rate_input and await check_rate_actual(rate=rate_input):
        rate_value_input = rate_input.value
    # source default
    if not rate_value_input:
        rate_value_input = await rate_get_default(currency=currency_input, rate_type=RateTypes.INPUT)
    # source other
    if not rate_value_input:
        rate_input = await RateRepository().get(
            currency=currency_input,
            type=RateTypes.INPUT,
        )
        if rate_input and await check_rate_actual(rate=rate_input):
            rate_value_input = rate_input.value
    # finish check
    if not rate_value_input:
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
    if rate_output and await check_rate_actual(rate=rate_output):
        rate_value_output = rate_output.value
    # source default
    if not rate_value_output:
        rate_value_output = await rate_get_default(currency=currency_output, rate_type=RateTypes.OUTPUT)
    # source other
    if not rate_value_output:
        rate_output = await RateRepository().get(
            currency=currency_output,
            type=RateTypes.OUTPUT,
        )
        if rate_output and await check_rate_actual(rate=rate_output):
            rate_value_output = rate_output.value
    # finish check
    if not rate_value_output:
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


async def check_rate_actual(rate: Rate) -> bool:
    rate_date = rate.created_at.replace(tzinfo=datetime.timezone.utc)
    date_now = datetime.datetime.now(tz=datetime.timezone.utc)
    date_delta = datetime.timedelta(minutes=settings.rate_actual_minutes)
    date_check = date_now - date_delta
    if rate_date < date_check:
        return False
    return True


async def rate_keep_pair_our():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
