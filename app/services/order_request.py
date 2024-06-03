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
    OrderCanceledReasons, MessageRoles, NotificationTypes
from app.repositories.order import OrderRepository
from app.repositories.order_request import OrderRequestRepository
from app.repositories.wallet_account import WalletAccountRepository
from app.services.base import BaseService
from app.services.wallet import WalletService
from app.utils.bot.notification import BotNotification
from app.utils.decorators import session_required
from app.utils.exceptions import OrderStateWrong, OrderNotPermission, OrderRequestStateNotPermission, \
    OrderRequestAlreadyExists
from app.utils.service_addons.order_request import order_request_update_type_cancel, \
    order_request_update_type_update_value, order_request_update_type_recreate
from app.utils.service_addons.wallet import wallet_check_permission
from app.utils.websockets.aiohttp import ConnectionManagerAiohttp


class OrderRequestService(BaseService):
    model = OrderRequest

    @session_required(return_token=True)
    async def create(
            self,
            session: Session,
            token: str,
            order_id: int,
            type_: str,
            value: int,
    ) -> dict:
        account = session.account
        order = await OrderRepository().get_by_id(id_=order_id)
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
        if await WalletAccountRepository().get(account=account, wallet=order.request.wallet):
            wallet = order.request.wallet
        else:
            wallet = order.requisite.wallet
        need_states = [OrderStates.PAYMENT, OrderStates.CONFIRMATION]
        if order.state not in need_states:
            raise OrderStateWrong(
                kwargs={
                    'id_value': order.id,
                    'state': order.state,
                    'need_state': f'/'.join(need_states),
                },
            )
        order_request, data = None, {}
        await self.check_have_order_request(order=order)
        connections_manager_aiohttp = ConnectionManagerAiohttp(token=token, order_id=order.id)
        if type_ == OrderRequestTypes.CANCEL:
            if order.state in OrderStates.choices_one_side_cancel and wallet.id == order.request.wallet.id:
                order_request = await OrderRequestRepository().create(
                    wallet=wallet,
                    order=order,
                    type=type_,
                    state=OrderRequestStates.WAIT,
                    data=data,
                )
                await connections_manager_aiohttp.send(
                    role=MessageRoles.SYSTEM,
                    text=f'order_request_create_{type_}',
                )
                await order_request_update_type_cancel(
                    order_request=order_request,
                    state=OrderRequestStates.COMPLETED,
                    canceled_reason=OrderCanceledReasons.ONE_SIDED,
                    connections_manager_aiohttp=connections_manager_aiohttp,
                )
        elif type_ == OrderRequestTypes.RECREATE:
            if order.state in OrderStates.choices_one_side_cancel and wallet.id == order.request.wallet.id:
                order_request = await OrderRequestRepository().create(
                    wallet=wallet,
                    order=order,
                    type=type_,
                    state=OrderRequestStates.WAIT,
                    data=data,
                )
                await connections_manager_aiohttp.send(
                    role=MessageRoles.SYSTEM,
                    text=f'order_request_create_{type_}',
                )
                await order_request_update_type_recreate(
                    order_request=order_request,
                    state=OrderRequestStates.COMPLETED,
                    canceled_reason=OrderCanceledReasons.ONE_SIDED,
                    connections_manager_aiohttp=connections_manager_aiohttp,
                )
        elif type_ == OrderRequestTypes.UPDATE_VALUE:
            data['currency_value'] = value
        if not order_request:
            order_request = await OrderRequestRepository().create(
                wallet=wallet,
                order=order,
                type=type_,
                state=OrderRequestStates.WAIT,
                data=data,
            )
            await connections_manager_aiohttp.send(
                role=MessageRoles.SYSTEM,
                text=f'order_request_create_{type_}',
            )
            bot_notification = BotNotification()
            await bot_notification.send_notification_by_wallet(
                wallet=order.request.wallet,
                notification_type=NotificationTypes.ORDER,
                text_key=f'notification_order_request_create_{type_}',
                order_id=order.id,
            )
            await bot_notification.send_notification_by_wallet(
                wallet=order.requisite.wallet,
                notification_type=NotificationTypes.ORDER,
                text_key=f'notification_order_request_create_{type_}',
                order_id=order.id,
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
        return {
            'id': order_request.id,
        }

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        order_request = await OrderRequestRepository().get_by_id(id_=id_)
        order = order_request.order
        await wallet_check_permission(
            account=account,
            wallets=[order.request.wallet, order.requisite.wallet],
            exception=OrderNotPermission(
                kwargs={
                    'field': 'OrderRequest',
                    'id_value': order_request.id
                },
            ),
        )
        return {
            'order_request': await self.generate_order_request_dict(order_request=order_request),
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
            order_id: int,
    ) -> dict:
        account = session.account
        order = await OrderRepository().get_by_id(id_=order_id)
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
            'orders_requests': [
                await self.generate_order_request_dict(order_request=order_request)
                for order_request in await OrderRequestRepository().get_list(order=order)
            ]
        }

    @session_required(return_token=True)
    async def update(
            self,
            session: Session,
            token: str,
            id_: int,
            state: str
    ) -> dict:
        account = session.account
        order_request = await OrderRequestRepository().get_by_id(id_=id_, state=OrderRequestStates.WAIT)
        order = order_request.order
        await wallet_check_permission(
            account=account,
            wallets=[order.request.wallet, order.requisite.wallet],
            exception=OrderNotPermission(
                kwargs={
                    'field': 'OrderRequest',
                    'id_value': order_request.id
                },
            ),
        )
        if await WalletAccountRepository().get(account=account, wallet=order.request.wallet):
            wallet = order.request.wallet
        else:
            wallet = order.requisite.wallet
        if wallet.id == order_request.wallet.id:
            raise OrderRequestStateNotPermission(
                kwargs={
                    'id_value': order_request.id,
                    'action': f'Change OrderRequest to state "{state}"',
                },
            )
        connections_manager_aiohttp = ConnectionManagerAiohttp(token=token, order_id=order.id)
        if order_request.type == OrderRequestTypes.CANCEL:
            await order_request_update_type_cancel(
                order_request=order_request,
                state=state,
                canceled_reason=OrderCanceledReasons.TWO_SIDED,
                connections_manager_aiohttp=connections_manager_aiohttp,
            )
        elif order_request.type == OrderRequestTypes.RECREATE:
            await order_request_update_type_recreate(
                order_request=order_request,
                state=state,
                canceled_reason=OrderCanceledReasons.TWO_SIDED,
                connections_manager_aiohttp=connections_manager_aiohttp,
            )
        elif order_request.type == OrderRequestTypes.UPDATE_VALUE:
            await order_request_update_type_update_value(
                order_request=order_request,
                state=state,
                connections_manager_aiohttp=connections_manager_aiohttp,
            )
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

    @session_required(permissions=['orders'], can_root=True)
    async def delete_by_admin(
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
            raise OrderRequestAlreadyExists(
                kwargs={
                    'id_': order_request.id,
                    'state': order_request.state,
                },
            )

    @staticmethod
    async def generate_order_request_dict(order_request: OrderRequest):
        return {
            'id': order_request.id,
            'wallet': await WalletService().generate_wallet_dict(wallet=order_request.wallet),
            'type': order_request.type,
            'state': order_request.state,
            'data': order_request.data,
        }
