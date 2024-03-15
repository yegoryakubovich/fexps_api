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
from app.utils.service_addons.method import method_check_input_field
from app.utils.service_addons.order import order_compete_related
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
            exception=OrderNotPermission(
                kwargs={
                    'field': 'Order',
                    'id_value': order.id
                },
            ),
        )
        return {
            'order': self._generate_order_dict(order=order)
        }

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
            exception=OrderNotPermission(
                kwargs={
                    'field': 'Request',
                    'id_value': request.id
                },
            ),
        )
        return {
            'orders': [
                self._generate_order_dict(order=order) for order in await OrderRepository().get_list(request=request)
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
                self._generate_order_dict(order=order) for order in
                await OrderRepository().get_list(requisite=requisite)
            ]
        }

    @staticmethod
    def _generate_order_dict(order: Order):
        return {
            'id': order.id,
            'type': order.type,
            'state': order.state,
            'canceled_reason': order.canceled_reason,
            'request': order.request_id,
            'requisite': order.requisite_id,
            'currency': order.requisite.currency.id_str,
            'currency_value': order.currency_value,
            'value': order.value,
            'rate': order.rate,
            'requisite_fields': order.requisite_fields,
            'input_fields': order.input_fields,
        }

    @session_required(permissions=['orders'])
    async def update_confirmation(
            self,
            session: Session,
            id_: int,
            input_fields: dict,
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
            await method_check_input_field(
                method=order.requisite.output_requisite_data.method,
                fields=input_fields,
            )
        elif order.type == OrderTypes.OUTPUT:
            await method_check_input_field(
                method=order.requisite.input_method,
                fields=input_fields,
            )
        await OrderRepository().update(
            order,
            input_fields=input_fields,
            state=next_state,
        )
        await self.create_action(
            model=order,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'state': next_state,
                'input_fields': input_fields,
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
