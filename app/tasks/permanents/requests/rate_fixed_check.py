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

from app.db.models import RequestStates, Actions, Request, NotificationTypes
from app.repositories import ActionParameterRepository, RequestRepository
from app.services.action import ActionService
from app.services.request import RequestService
from app.tasks.permanents.requests.logger import RequestLogger
from app.utils.bot.notification import BotNotification
from config import settings

custom_logger = RequestLogger(prefix='request_rate_fixed_check')


async def run():
    time_now = datetime.datetime.now(datetime.UTC)
    for request in await RequestRepository().get_list_not_finished(rate_fixed=True):
        request_action = await get_action_by_state(request, state=RequestStates.INPUT_RESERVATION)
        if not request_action:
            continue
        request_action_delta = time_now.replace(tzinfo=None) - request_action.datetime.replace(tzinfo=None)
        if request_action_delta >= datetime.timedelta(minutes=settings.request_rate_fixed_minutes):
            custom_logger.info(text=f'rate_fixed=False', request=request)
            await RequestService().rate_fixed_off(request=request)
            await BotNotification().send_notification_by_wallet(
                wallet=request.wallet,
                notification_type=NotificationTypes.REQUEST,
                text_key=f'notification_request_rate_fixed_stop',
                request_id=request.id,
            )
        await asyncio.sleep(1)
    await asyncio.sleep(5)


async def get_action_by_state(request: Request, state: str):
    actions_update = await ActionService().get_actions(request, action=Actions.UPDATE)
    if not actions_update:
        return
    for action in actions_update:
        action_param = await ActionParameterRepository().get(action=action, key='state', value=state)
        if not action_param:
            continue
        return action


async def request_rate_fixed_check():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
