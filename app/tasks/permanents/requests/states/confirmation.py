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

from app.db.models import RequestStates, Actions, NotificationTypes, RequestTypes, WalletBanReasons
from app.repositories import WalletBanRequestRepository, RequestRepository
from app.services.action import ActionService
from app.services.wallet_ban import WalletBanService
from app.tasks.permanents.requests.logger import RequestLogger
from app.utils.bot.notification import BotNotification
from config import settings

custom_logger = RequestLogger(prefix='request_confirmation_check')


async def run():
    time_now = datetime.datetime.now(datetime.UTC)
    for request in await RequestRepository().get_list_by_asc(state=RequestStates.CONFIRMATION):
        request_action = await ActionService().get_action(request, action=Actions.CREATE)
        if not request_action:
            continue
        request_action_delta = time_now - request_action.datetime.replace(tzinfo=datetime.UTC)
        if request_action_delta < datetime.timedelta(minutes=settings.request_confirmation_check):
            continue
        custom_logger.info(text=f'{request.state}->{RequestStates.CANCELED}', request=request)
        if request.type == RequestTypes.OUTPUT:
            wallet_ban = await WalletBanService().create_related(
                wallet=request.wallet,
                value=-request.output_value,
                reason=WalletBanReasons.BY_REQUEST,
            )
            await WalletBanRequestRepository().create(wallet_ban=wallet_ban, request=request)
        await RequestRepository().update(request, state=RequestStates.CANCELED)
        await BotNotification().send_notification_by_wallet(
            wallet=request.wallet,
            notification_type=NotificationTypes.REQUEST,
            text_key=f'notification_request_update_state_{RequestStates.CANCELED}',
            request_id=request.id,
        )
    await asyncio.sleep(1)


async def request_confirmation_check():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
