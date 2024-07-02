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

from app.db.models import RateTypes, RateSources, Method
from app.repositories import RateRepository, MethodRepository
from app.utils.calcs.rates.bybit import calcs_rate_bybit
from app.utils.calcs.rates.default import calcs_rate_default
from app.utils.calcs.rates.requisite import calcs_rate_requisite


async def rate_keep():
    logging.info('started')
    for method in await MethodRepository().get_list():
        await update_rate(method=method, rate_type=RateTypes.INPUT)
        await update_rate(method=method, rate_type=RateTypes.OUTPUT)
        await asyncio.sleep(0.5)


async def update_rate(method: Method, rate_type: str):
    rate = await calcs_rate_requisite(method=method, rate_type=rate_type)
    source = RateSources.REQUISITE
    if not rate:
        rate = await calcs_rate_default(method=method, rate_type=rate_type)
        source = RateSources.DEFAULT
    if not rate:
        rate = await calcs_rate_bybit(method=method, rate_type=rate_type)
        source = RateSources.BYBIT
    if not rate:
        return
    await RateRepository().create(method=method, type=rate_type, source=source, rate=rate)
