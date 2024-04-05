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
import datetime
import logging

from app.db.models import RequestStates, RequisiteStates
from app.repositories import RequisiteRepository
from app.repositories.request import RequestRepository
from config import settings

prefix = '[requisite_balance_out]'


async def requisite_balance_out_check():
    logging.critical(f'{prefix} start')
    while True:
        try:
            await run()
        except Exception as e:
            logging.error(f'{prefix}  Exception \n {e}')


async def run():
    # time_now = datetime.datetime.now(datetime.UTC)
    # for requisite in await RequisiteRepository().get_list(state=RequisiteStates.ENABLE):
    #     currency = requisite.currency
    #     request_action = await get_action_by_state(request, state=RequestStates.WAITING)
    #     if not request_action:
    #         logging.info(f'{prefix} Request.{request.id} not action')
    #         continue
    #     request_action_delta = time_now - request_action.datetime.replace(tzinfo=None)
    #     if request_action_delta >= datetime.timedelta(minutes=settings.request_rate_confirmed_minutes):
    #         await RequestRepository().update(request, rate_confirmed=False)
    #         logging.info(f'{prefix} Request.{request.id} rate_confirmed=False')
    #     await asyncio.sleep(0.25)
    await asyncio.sleep(10)
