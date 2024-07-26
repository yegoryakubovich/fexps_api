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

from app.db.models import Request, RequestStates, OrderTypes, OrderStates, RequestTypes, WalletBanReasons
from app.repositories import RequestRepository, OrderRepository, WalletBanRequestRepository
from app.services.notification import NotificationService
from app.services.transfer_system import TransferSystemService
from app.services.wallet_ban import WalletBanService


async def request_check_state_input(request: Request):
    logging.info(f'Request #{request.id}    start check')
    request = await RequestRepository().get_by_id(id_=request.id)
    if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.WAITING):
        logging.info(f'Request #{request.id}    {request.state}->{RequestStates.INPUT_RESERVATION}')
        await RequestRepository().update(request, state=RequestStates.INPUT_RESERVATION)
        return
    if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.PAYMENT):
        return
    if await OrderRepository().get_list(request=request, type=OrderTypes.INPUT, state=OrderStates.CONFIRMATION):
        return
    order_value_sum = sum([
        order.value if order.state != OrderStates.CANCELED else 0
        for order in await OrderRepository().get_list(request=request, type=OrderTypes.INPUT)
    ])
    difference_rate = request.difference_rate
    difference = order_value_sum - request.input_value
    if difference:
        await TransferSystemService().payment_difference(request=request, value=difference, from_banned_value=True)
        difference_rate += difference
    await TransferSystemService().payment_commission(request=request, from_banned_value=True)
    if request.type == RequestTypes.INPUT:
        result_input_value = request.input_value - request.commission
        wallet_ban = await WalletBanService().create_related(
            wallet=request.wallet,
            value=-result_input_value,
            reason=WalletBanReasons.BY_REQUEST,
        )
        await WalletBanRequestRepository().create(wallet_ban=wallet_ban, request=request)
    if request.type == RequestTypes.INPUT:
        logging.info(f'Request #{request.id}    {request.state}->{RequestStates.COMPLETED}')
        await RequestRepository().update(request, state=RequestStates.COMPLETED, difference_rate=difference_rate)
        await NotificationService().create_notification_request_complete(request=request)
    else:
        logging.info(f'Request #{request.id}    {request.state}->{RequestStates.OUTPUT_RESERVATION}')
        await RequestRepository().update(
            request,
            state=RequestStates.OUTPUT_RESERVATION,
            difference_rate=difference_rate,
        )
