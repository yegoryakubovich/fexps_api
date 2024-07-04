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

from app.db.models import Request, RequestStates, OrderTypes, OrderStates, NotificationTypes
from app.repositories import RequestRepository, OrderRepository
from app.services.transfer_system import TransferSystemService
from app.utils.bot.notification import BotNotification


async def request_check_state_output(request: Request):
    logging.info(f'Request #{request.id}    start check')
    request = await RequestRepository().get_by_id(id_=request.id)
    if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.WAITING):
        logging.info(f'Request #{request.id}    {request.state}->{RequestStates.OUTPUT_RESERVATION}')
        await RequestRepository().update(request, state=RequestStates.OUTPUT_RESERVATION)
        return
    if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.PAYMENT):
        return
    if await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT, state=OrderStates.CONFIRMATION):
        return
    order_value_sum = sum([
        order.value if order.state == OrderStates.COMPLETED else 0
        for order in await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT)
    ])
    difference_rate = request.difference_rate
    difference = request.output_value - order_value_sum
    if difference:
        await TransferSystemService().payment_difference(request=request, value=difference, from_banned_value=True)
        difference_rate += difference
    # if request.difference:
    #     await TransferSystemService().payment_difference(request=request, value=request.difference)
    logging.info(f'Request #{request.id}    {request.state}->{RequestStates.COMPLETED}')
    await RequestRepository().update(request, state=RequestStates.COMPLETED)
    await BotNotification().send_notification_by_wallet(
        wallet=request.wallet,
        notification_type=NotificationTypes.REQUEST,
        text_key=f'notification_request_update_state_{RequestStates.COMPLETED}',
        request_id=request.id,
    )
