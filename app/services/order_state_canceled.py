#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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


from app.db.models import Order, Session
from app.repositories.order import OrderRepository
from app.services.base import BaseService
from app.services.order_request import OrderRequestService
from app.utils.decorators import session_required


class OrderStatesCanceledService(BaseService):
    model = Order

    @session_required()
    async def update(
            self,
            session: Session,
            order_id: int,
    ) -> dict:
        order = await OrderRepository().get_by_id(id_=order_id)
        await OrderRequestService().check_have_order_request(order=order)
