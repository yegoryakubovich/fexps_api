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

from app.db.models import Currency, RateSources, RateTypes
from app.repositories import CurrencyRepository, RateParseRepository
from app.utils.parsers.bybit import parser_bybit_get


async def run():
    currency = await CurrencyRepository().get_by_id_str(id_str='rub')
    await update_rate(currency=currency, rate_type=RateTypes.INPUT)
    await update_rate(currency=currency, rate_type=RateTypes.OUTPUT)
    await asyncio.sleep(60)


async def update_rate(currency: Currency, rate_type: str):
    logging.info(f'update {currency.id_str.upper()} {rate_type}')
    rate = await parser_bybit_get(currency=currency, rate_type=rate_type)
    if not rate:
        return
    await RateParseRepository().create(
        currency=currency,
        type=rate_type,
        source=RateSources.BYBIT,
        rate=rate,
    )
    await asyncio.sleep(0.25)


async def rate_keep_bybit_parse():
    logging.info(f'started rate_keep_bybit_parse')
    while True:
        try:
            await run()
        except ValueError as e:
            logging.critical(f'Exception \n {e}')
