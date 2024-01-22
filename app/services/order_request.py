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


from app.db.models import Session, Actions, OrderRequest
from app.repositories.order import OrderRepository
from app.repositories.order_request import OrderRequestRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class OrderRequestService(BaseService):
    model = OrderRequest

    @session_required()
    async def create(
            self,
            session: Session,
            order_id: int,
            type_: str,
            canceled_reason: str,
    ) -> dict:
        order = await OrderRepository().get_by_id(id_=order_id)

        order_request = await OrderRequestRepository().create(
            type=type_,
            canceled_reason=canceled_reason,
        )
        await self.create_action(
            model=order_request,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'name_text': name_text.key,
                'currency': currency.id_str
            },
        )

        return {'method_id': method.id}
