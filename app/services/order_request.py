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


from app.db.models import Session, Actions, OrderRequest, OrderRequestTypes, OrderRequestStates, Order
from app.repositories.order import OrderRepository, OrderRequestValidationError
from app.repositories.order_request import OrderRequestRepository, OrderRequestFound
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
        data = {}
        if type_ == OrderRequestTypes.CANCEL:
            if not canceled_reason:
                raise OrderRequestValidationError('Parameter "canceled_reason" not found')
            data['canceled_reason'] = canceled_reason

        order_request = await OrderRequestRepository().create(
            order=order,
            type=type_,
            state=OrderRequestStates.WAIT,
            data=data,
        )
        await self.create_action(
            model=order_request,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'order_id': order_id,
                'type_': type_,
                'canceled_reason': canceled_reason,
            },
        )

        return {'order_request_id': order_request.id}

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            is_result: bool
    ) -> dict:
        order_request = await OrderRequestRepository().get_by_id(id_=id_)
        if is_result:
            await OrderRequestRepository().update(order_request, state=OrderRequestStates.COMPLETED)
        else:
            await OrderRequestRepository().update(order_request, state=OrderRequestStates.CANCELED)
        await self.create_action(
            model=order_request,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'id': id_,
                'is_result': is_result,
            },
        )

        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        order_request = await OrderRequestRepository().get_by_id(id_=id_)
        await OrderRequestRepository().delete(order_request)
        await self.create_action(
            model=order_request,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )

        return {}

    @staticmethod
    async def check_have_order_request(order: Order) -> None:
        order_request = await OrderRequestRepository().get(order=order, state=OrderRequestStates.WAIT)
        if order_request:
            raise OrderRequestFound(f'Found order_request.{order_request.id} in status "{OrderRequestStates.WAIT}"')
