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
import logging
import math

import aiohttp

from app.db.models import RateTypes, Currency


# sbp: 382,
# tinkoff: 581,
# sberbank: 585,


async def rate_get_bybit(currency: Currency, rate_type: str = 'output'):
    rates = []
    async with aiohttp.ClientSession() as session:
        for payment_id in [382, 581, 585]:
            response = await session.post(
                url='https://api2.bybit.com/fiat/otc/item/online',
                json={
                    'userId': '',
                    'tokenId': 'USDT',
                    'currencyId': currency.id_str.upper(),
                    'side': '0' if rate_type == RateTypes.INPUT else '1',
                    'payment': [str(payment_id)],
                    'size': '5',
                    'page': '1',
                    'amount': '200000',
                    'authMaker': True,
                },
            )
            json_data = await response.json()
            logging.critical(json_data)
            rates += [float(item['price']) for item in json_data['result']['items']]
    print(rates)
    print(sum(rates) / len(rates))
    rate_value = sum(rates) / len(rates)
    if rate_type == RateTypes.INPUT:
        rate_value = math.floor(rate_value * 10 ** currency.rate_decimal)
    elif rate_type == RateTypes.OUTPUT:
        rate_value = math.ceil(rate_value * 10 ** currency.rate_decimal)
    return rate_value