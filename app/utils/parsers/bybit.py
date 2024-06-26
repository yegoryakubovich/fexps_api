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


import math

import aiohttp

from app.db.models import RateTypes, Currency

VALUES_LIST = [
    # 50_000,
    100_000,
    # 150_000,
]
PAYMENT_IDS_LIST = [
    # 382,  # SBP
    581,  # T-BANK
    # 595,  # SBERBANK,
]


async def parser_bybit_get(
        currency: Currency,
        rate_type: str,
        token_id: str = 'USDT',
):
    rates = []
    async with aiohttp.ClientSession() as session:
        for value in VALUES_LIST:
            for payment_id in PAYMENT_IDS_LIST:
                response = await session.post(
                    url='https://api2.bybit.com/fiat/otc/item/online',
                    json={
                        'userId': '',
                        'tokenId': token_id,
                        'currencyId': currency.id_str.upper(),
                        'side': '1' if rate_type == RateTypes.INPUT else '0',
                        'payment': [str(payment_id)],
                        'size': '5',
                        'page': '1',
                        'amount': str(value),
                        'authMaker': True,
                    },
                )
                response_json = await response.json()
                rates += [float(item['price']) for item in response_json['result']['items']]
    if not rates:
        return
    rate_value = sum(rates) / len(rates)
    if rate_type == RateTypes.INPUT:
        rate_value = math.ceil(rate_value * 10 ** currency.rate_decimal)
    elif rate_type == RateTypes.OUTPUT:
        rate_value = math.floor(rate_value * 10 ** currency.rate_decimal)
    return rate_value
