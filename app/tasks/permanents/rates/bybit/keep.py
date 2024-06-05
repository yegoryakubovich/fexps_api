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

from app.db.models import Currency, RateSources, RateTypes
from app.repositories import CurrencyRepository, RateRepository
from app.tasks.permanents.rates.bybit.utils import rate_get_bybit
from app.tasks.permanents.rates.logger import RateLogger

custom_logger = RateLogger(prefix='rate_bybit_keep')


async def rate_keep_bybit():
    currency = await CurrencyRepository().get_by_id_str(id_str='rub')
    await update_rate(currency=currency, rate_type=RateTypes.INPUT)
    await update_rate(currency=currency, rate_type=RateTypes.OUTPUT)


async def update_rate(currency: Currency, rate_type: str):
    result_rate = await rate_get_bybit(currency=currency, rate_type=rate_type)
    if not result_rate:
        return
    await RateRepository().create(
        currency=currency,
        type=rate_type,
        source=RateSources.BYBIT,
        value=result_rate,
    )
