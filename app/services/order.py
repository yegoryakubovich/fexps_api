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


from app.db.models import Session, Order, OrderTypes, OrderStates, Actions
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.repositories.requisite import RequisiteRepository
from app.services.base import BaseService
from app.services.order_request import OrderRequestService
from app.utils.decorators import session_required
from app.utils.exceptions.order import OrderNotPermission, OrderStateWrong, OrderStateNotPermission
from app.utils.service_addons.method import method_check_confirmation_field
from app.utils.service_addons.order import order_compete_related, get_order_dict
from app.utils.service_addons.wallet import wallet_check_permission


class OrderService(BaseService):
    model = Order

    @session_required(permissions=['orders'])
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        order = await OrderRepository().get_by_id(id_=id_)
        await wallet_check_permission(
            account=account,
            wallets=[order.request.wallet, order.requisite.wallet],
            exception=OrderNotPermission(kwargs={'field': 'Order', 'id_value': order.id}),
        )
        return {'order': get_order_dict(order=order)}

    @session_required(permissions=['orders'])
    async def get_all_by_request(
            self,
            session: Session,
            request_id: int,
    ) -> dict:
        account = session.account
        request = await RequestRepository().get_by_id(id_=request_id)
        await wallet_check_permission(
            account=account,
            wallets=[request.wallet],
            exception=OrderNotPermission(kwargs={'field': 'Request', 'id_value': request.id}),
        )
        return {
            'orders': [
                get_order_dict(order=order) for order in await OrderRepository().get_list(request=request)
            ]
        }

    @session_required(permissions=['orders'])
    async def get_all_by_requisite(
            self,
            session: Session,
            requisite_id: int,
    ) -> dict:
        account = session.account
        requisite = await RequisiteRepository().get_by_id(id_=requisite_id)
        await wallet_check_permission(
            account=account,
            wallets=[requisite.wallet],
            exception=OrderNotPermission(kwargs={'field': 'Requisite', 'id_value': requisite.id}),
        )
        return {
            'orders': [
                get_order_dict(order=order) for order in await OrderRepository().get_list(requisite=requisite)
            ]
        }

    @session_required(permissions=['orders'])
    async def update_confirmation(
            self,
            session: Session,
            id_: int,
            confirmation_fields: dict,
    ) -> dict:
        account = session.account
        need_state = OrderStates.PAYMENT
        next_state = OrderStates.CONFIRMATION
        order = await OrderRepository().get_by_id(id_=id_)
        if order.type == OrderTypes.INPUT:
            await wallet_check_permission(
                account=account,
                wallets=[order.request.wallet],
                exception=OrderStateNotPermission(
                    kwargs={
                        'id_value': order.id,
                        'action': f'Update state to {next_state}',
                    }
                )
            )
        elif order.type == OrderTypes.OUTPUT:
            await wallet_check_permission(
                account=account,
                wallets=[order.requisite.wallet],
                exception=OrderStateNotPermission(
                    kwargs={
                        'id_value': order.id,
                        'action': f'Update state to {next_state}',
                    }
                )
            )
        if order.state != need_state:
            raise OrderStateWrong(
                kwargs={
                    'id_value': order.id,
                    'state': order.state,
                    'need_state': need_state,
                },
            )
        await OrderRequestService().check_have_order_request(order=order)
        if order.type == OrderTypes.INPUT:
            await method_check_confirmation_field(
                method=order.requisite.output_requisite_data.method,
                fields=confirmation_fields,
            )
        elif order.type == OrderTypes.OUTPUT:
            await method_check_confirmation_field(
                method=order.requisite.input_method,
                fields=confirmation_fields,
            )
        await OrderRepository().update(
            order,
            confirmation_fields=confirmation_fields,
            state=next_state,
        )
        await self.create_action(
            model=order,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'state': next_state,
                'confirmation_fields': confirmation_fields,
            },
        )
        return {}

    @session_required(permissions=['orders'])
    async def update_completed(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        need_state = OrderStates.CONFIRMATION
        next_state = OrderStates.COMPLETED
        order = await OrderRepository().get_by_id(id_=id_)
        if order.type == OrderTypes.INPUT:
            await wallet_check_permission(
                account=account,
                wallets=[order.requisite.wallet],
                exception=OrderStateNotPermission(
                    kwargs={
                        'id_value': order.id,
                        'action': f'Update state to {next_state}',
                    }
                )
            )
        elif order.type == OrderTypes.OUTPUT:
            await wallet_check_permission(
                account=account,
                wallets=[order.request.wallet],
                exception=OrderStateNotPermission(
                    kwargs={
                        'id_value': order.id,
                        'action': f'Update state to {next_state}',
                    }
                )
            )
        if order.state != need_state:
            raise OrderStateWrong(
                kwargs={
                    'id_value': order.id,
                    'state': order.state,
                    'need_state': need_state,
                },
            )
        await OrderRequestService().check_have_order_request(order=order)
        await order_compete_related(order=order)
        await OrderRepository().update(order, state=next_state)
        await self.create_action(
            model=order,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'state': next_state,
            },
        )
        return {}

    @session_required(permissions=['orders'])
    async def update_payment(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        need_state = OrderStates.CONFIRMATION
        next_state = OrderStates.PAYMENT
        order = await OrderRepository().get_by_id(id_=id_)
        if order.type == OrderTypes.INPUT:
            await wallet_check_permission(
                account=account,
                wallets=[order.requisite.wallet],
                exception=OrderStateNotPermission(
                    kwargs={
                        'id_value': order.id,
                        'action': f'Update state to {next_state}',
                    }
                )
            )
        elif order.type == OrderTypes.OUTPUT:
            await wallet_check_permission(
                account=account,
                wallets=[order.request.wallet],
                exception=OrderStateNotPermission(
                    kwargs={
                        'id_value': order.id,
                        'action': f'Update state to {next_state}',
                    }
                )
            )
        if order.state != need_state:
            raise OrderStateWrong(
                kwargs={
                    'id_value': order.id,
                    'state': order.state,
                    'need_state': need_state,
                },
            )
        await OrderRequestService().check_have_order_request(order=order)
        await OrderRepository().update(order, state=next_state)
        await self.create_action(
            model=order,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'state': next_state,
            },
        )
        return {}
