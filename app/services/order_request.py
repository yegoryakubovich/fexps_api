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


from app.db.models import Session, Actions, OrderRequest, OrderRequestTypes, OrderRequestStates, Order, OrderStates, \
    OrderCanceledReasons
from app.repositories.order import OrderRepository
from app.repositories.order_request import OrderRequestRepository
from app.repositories.wallet_account import WalletAccountRepository
from app.services.base import BaseService
from app.services.order import OrderService
from app.utils.decorators import session_required
from app.utils.exaptions.order import OrderRequestValidationError, OrderRequestFound


class OrderRequestService(BaseService):
    model = OrderRequest

    @session_required(permissions=['orders'])
    async def create(
            self,
            session: Session,
            order_id: int,
            type_: str,
            value: int,
    ) -> dict:
        order = await OrderRepository().get_by_id(id_=order_id)
        order_request = None
        await self.check_have_order_request(order=order)
        data = {}
        if type_ == OrderRequestTypes.CANCEL:
            if order.state in OrderStates.choices_one_side_cancel:
                wallet_account = await WalletAccountRepository().get(wallet=order.request.wallet)
                if wallet_account and session.account_id == wallet_account.account_id:
                    order_request = await OrderRequestRepository().create(
                        order=order,
                        type=type_,
                        state=OrderRequestStates.COMPLETED,
                        data=data,
                    )
                    await self.update_type_cancel(
                        order_request=order_request,
                        state=OrderRequestStates.CANCELED,
                        canceled_reason=OrderCanceledReasons.ONE_SIDED,
                    )
        elif type_ == OrderRequestTypes.UPDATE_VALUE:
            if not value:
                raise OrderRequestValidationError('Parameter "value" not found')
            data['value'] = value

        if not order_request:
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
                'value': value,
            },
        )

        return {'order_request_id': order_request.id}

    @session_required(permissions=['orders'])
    async def update(
            self,
            session: Session,
            id_: int,
            state: str
    ) -> dict:
        order_request = await OrderRequestRepository().get_by_id(id_=id_, state=OrderRequestStates.WAIT)
        if order_request.type == OrderRequestTypes.CANCEL:
            await self.update_type_cancel(
                order_request=order_request, state=state, canceled_reason=OrderCanceledReasons.TWO_SIDED,
            )
        elif order_request.type == OrderRequestTypes.UPDATE_VALUE:
            await self.update_type_update_value(order_request=order_request, state=state)

        await OrderRequestRepository().update(order_request, state=state)
        await self.create_action(
            model=order_request,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'id': id_,
                'state': state,
            },
        )

        return {}

    @staticmethod
    async def update_type_cancel(order_request: OrderRequest, state: str, canceled_reason: str):
        if state == OrderRequestStates.COMPLETED:
            await OrderService().cancel_related(order=order_request.order)
            await OrderRepository().update(
                order_request.order,
                state=OrderStates.CANCELED,
                canceled_reason=canceled_reason,
            )
        elif state == OrderRequestStates.CANCELED:
            pass

    @staticmethod
    async def update_type_update_value(order_request: OrderRequest, state: str):
        if state == OrderRequestStates.COMPLETED:
            pass
        elif state == OrderRequestStates.CANCELED:
            pass

    @session_required(permissions=['orders'])
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
