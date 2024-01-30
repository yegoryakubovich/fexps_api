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


from app.db.models import Order, Session, OrderStates, Actions
from app.repositories.order import OrderRepository
from app.services.base import BaseService
from app.services.method import MethodService
from app.services.order_request import OrderRequestService
from app.services.request import RequestService
from app.utils.decorators import session_required


class OrderStatesConfirmationService(BaseService):
    model = Order

    @session_required(permissions=['orders'])  # Получатель может вернуть в payment
    async def update(
            self,
            session: Session,
            id_: int,
            confirmation_fields: dict,
    ) -> dict:
        order = await OrderRepository().get_by_id(id_=id_)
        await OrderRequestService().check_have_order_request(order=order)
        await MethodService().check_confirmation_field(
            method=order.requisite.requisite_data.method, fields=confirmation_fields,
        )

        await OrderRepository().update(
            order,
            confirmation_fields=confirmation_fields,
            state=OrderStates.CONFIRMATION,
        )
        await self.create_action(
            model=order,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'state': OrderStates.CONFIRMATION,
                'confirmation_fields': confirmation_fields,
            },
        )
        await RequestService().check_all_orders(request=order.request)

        return {}
