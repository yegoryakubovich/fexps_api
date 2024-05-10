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
import math

from app.db.models import RequisiteTypes, RequisiteStates, Currency
from app.repositories import CurrencyRepository, RequisiteRepository, RatePairRepository
from app.tasks.permanents.rates.logger import RateLogger

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
    requisites_input = await RequisiteRepository().get_list_input_by_rate(
        currency=currency_input,
        type=RequisiteTypes.OUTPUT,
        state=RequisiteStates.ENABLE,
    )
    if not requisites_input:
        return
    requisites_output = await RequisiteRepository().get_list_output_by_rate(
        currency=currency_output,
        type=RequisiteTypes.INPUT,
        state=RequisiteStates.ENABLE,
    )
    if not requisites_output:
        return
    rate_decimal = max([currency_input.rate_decimal, currency_output.rate_decimal])
    rate_input_value = requisites_input[0].rate * 10 ** (rate_decimal - currency_input.rate_decimal)
    rate_output_value = requisites_output[0].rate * 10 ** (rate_decimal - currency_output.rate_decimal)
    rate_value = math.ceil(rate_input_value / rate_output_value * 10 ** rate_decimal)
    await RatePairRepository().create(
        currency_input=currency_input,
        currency_output=currency_output,
        rate_decimal=rate_decimal,
        value=rate_value,
    )


async def rate_keep_pair():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
