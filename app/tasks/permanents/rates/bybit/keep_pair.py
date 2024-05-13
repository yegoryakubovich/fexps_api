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

from app.db.models import Currency, RateSources
from app.repositories import CurrencyRepository, RatePairRepository
from app.tasks.permanents.rates.bybit.utils import rate_get_bybit
from app.tasks.permanents.rates.logger import RateLogger

custom_logger = RateLogger(prefix='rate_bybit_keep')


async def run():
    currency = await CurrencyRepository().get_by_id_str(id_str='rub')
    currency_usdt = await CurrencyRepository().get_by_id_str(id_str='usdt')
    await update_rate(currency=currency, currency_usdt=currency_usdt, type_='input')
    await update_rate(currency=currency, currency_usdt=currency_usdt, type_='output')
    await asyncio.sleep(60)


async def update_rate(currency: Currency, currency_usdt: Currency, type_: str):
    rate_value = await rate_get_bybit(currency=currency, type_=type_)
    rate_decimal = max([currency.rate_decimal, currency_usdt.rate_decimal])
    if not rate_value:
        return
    params = {}
    if type_ == 'input':
        params = {
            'currency_input': currency,
            'currency_output': currency_usdt,
        }
    elif type_ == 'output':
        params = {
            'currency_input': currency_usdt,
            'currency_output': currency,
        }
    if not params:
        return
    await RatePairRepository().create(**params, source=RateSources.BYBIT, rate_decimal=rate_decimal, value=rate_value)


async def rate_keep_pair_bybit():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
