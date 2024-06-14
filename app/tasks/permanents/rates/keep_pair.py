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

from app.db.models import Method
from app.repositories import CurrencyRepository, RatePairRepository, MethodRepository, CommissionPackRepository
from app.tasks.permanents.rates.logger import RateLogger
from app.utils.calculations.rates.basic.data_all import calculate_data_all_by_input_value

custom_logger = RateLogger(prefix='rate_keep_pair')


async def rate_keep_pair():
    input_methods: list[Method] = []
    for input_currency in await CurrencyRepository().get_list():
        input_methods += [
            input_method
            for input_method in await MethodRepository().get_list(currency=input_currency)
        ]
    output_methods: list[Method] = []
    for output_currency in await CurrencyRepository().get_list():
        output_methods += [
            output_method
            for output_method in await MethodRepository().get_list(currency=output_currency)
        ]
    for input_method in input_methods:
        for output_method in output_methods:
            if input_method.currency.id_str == output_method.currency.id_str:
                continue
            await update_rate(input_method=input_method, output_method=output_method)
            await asyncio.sleep(0.1)
        await asyncio.sleep(0.25)


async def update_rate(input_method: Method, output_method: Method):
    commission_pack = await CommissionPackRepository().get(is_default=True)
    result = await calculate_data_all_by_input_value(
        input_method=input_method,
        output_method=output_method,
        commission_pack=commission_pack,
        input_value=3_000_00,
    )
    if not result:
        return
    await RatePairRepository().create(
        input_method=input_method,
        output_method=output_method,
        rate_decimal=result.rate_decimal,
        rate=result.rate,
    )
