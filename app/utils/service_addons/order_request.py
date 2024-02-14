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


from app.db.models import Request, OrderTypes, OrderStates, Order, Requisite, WalletBanReasons, Wallet, TransferTypes, \
    OrderRequest, OrderRequestStates
from app.repositories.order import OrderRepository
from app.repositories.order_request import OrderRequestRepository
from app.repositories.request import RequestRepository
from app.repositories.requisite import RequisiteRepository
from app.services.wallet_ban import WalletBanService
from app.utils.calculations.schemes.loading import RequisiteScheme
from app.utils.service_addons.order import order_cancel_related
from app.utils.service_addons.transfer import create_transfer


async def order_request_update_type_cancel(order_request: OrderRequest, state: str, canceled_reason: str):
    if state == OrderRequestStates.COMPLETED:
        await order_cancel_related(order=order_request.order)
        await OrderRepository().update(
            order_request.order,
            state=OrderStates.CANCELED,
            canceled_reason=canceled_reason,
        )
        await OrderRequestRepository().update(order_request, state=state)
        await RequestRepository().update(order_request.order.request, rate_confirmed=False)
    elif state == OrderRequestStates.CANCELED:
        await OrderRequestRepository().update(order_request, state=state)


async def order_request_update_type_update_value(order_request: OrderRequest, state: str):
    if state == OrderRequestStates.COMPLETED:
        """CHANGE VALUE LOGIC"""
        await OrderRequestRepository().update(order_request, state=state)
        await RequestRepository().update(order_request.order.request, rate_confirmed=False)
    elif state == OrderRequestStates.CANCELED:
        await OrderRequestRepository().update(order_request, state=state)