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

from app.db.models import RequisiteTypes, RequisiteStates, RateTypes, Currency, RateSources
from app.repositories import CurrencyRepository, RequisiteRepository, RateRepository
from app.tasks.permanents.rates.logger import RateLogger

custom_logger = RateLogger(prefix='rate_our_keep')


async def run():
    for currency in await CurrencyRepository().get_list():
        await update_rate(currency=currency, rate_type=RateTypes.INPUT)
        await update_rate(currency=currency, rate_type=RateTypes.OUTPUT)
        await asyncio.sleep(1)
    await asyncio.sleep(60)


async def update_rate(currency: Currency, rate_type: str):
    requisites = None
    if rate_type == RateTypes.INPUT:
        requisites = await RequisiteRepository().get_list_input_by_rate(
            currency=currency,
            type=RequisiteTypes.OUTPUT,
            state=RequisiteStates.ENABLE,
        )
    elif rate_type == RateTypes.OUTPUT:
        requisites = await RequisiteRepository().get_list_output_by_rate(
            currency=currency,
            type=RequisiteTypes.INPUT,
            state=RequisiteStates.ENABLE,
        )
    if not requisites:
        return
    rate_value = requisites[0].rate
    await RateRepository().create(
        currency=currency,
        type=rate_type,
        source=RateSources.OUR,
        value=rate_value,
    )


async def rate_our_keep():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
