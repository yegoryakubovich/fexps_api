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

from app.tasks.permanents.utils.fexps_api_client import fexps_api_client


async def rate_parse_bybit():
    logging.info(f'start rate_parse_bybit')
    while True:
        try:
            await fexps_api_client.task.rates.parsers.bybit()
            await asyncio.sleep(60)
        except ValueError as e:
            logging.critical(f'Exception \n {e}')
