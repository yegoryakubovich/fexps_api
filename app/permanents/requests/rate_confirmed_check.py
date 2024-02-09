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
from datetime import datetime, timedelta

from app.db.models import RequestStates, Actions, Request, RequestTypes
from app.repositories.action_parameter import ActionParameterRepository
from app.repositories.request import RequestRepository
from app.services import ActionService
from config import settings

prefix = '[request_rate_confirmed_check]'


async def request_rate_confirmed_check():
    while True:
        try:
            await run()
        except Exception as e:
            logging.error(f'{prefix}  Exception \n {e}')


async def run():
    time_now = datetime.utcnow()
    for request in await RequestRepository().get_list_by_asc():
        if request.state not in RequestStates.choices_rate_confirmation:
            continue
        request_action = await get_action_by_state(request, state=RequestStates.WAITING)
        if not request_action:
            continue
        request_action_delta = time_now - request_action.datetime
        if request_action_delta >= timedelta(minutes=settings.request_rate_confirmed_minutes):
            await RequestRepository().update(request, rate_confirmed=False)
        await asyncio.sleep(0.125)
    await asyncio.sleep(0.25)
    await asyncio.sleep(0.5)


async def get_action_by_state(request: Request, state: str):
    actions_update = await ActionService().get_actions(request, action=Actions.UPDATE)
    if not actions_update:
        return
    for action in actions_update:
        action_param = await ActionParameterRepository().get(action=action, key='state', value=state)
        if not action_param:
            continue
        return action