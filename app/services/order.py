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


from app.db.models import Session, Order, Actions, Requisite, OrderTypes, Request, WalletBanReasons, OrderStates, \
    TransferTypes
from app.repositories.order import OrderRepository
from app.repositories.requisite import RequisiteRepository
from app.services.base import BaseService
from app.services.transfer import TransferService
from app.services.wallet_ban import WalletBanService
from app.utils.decorators import session_required


class OrderService(BaseService):
    model = Order

    @staticmethod
    async def create_related(
            order_type: str,
            request: Request,
            requisite: Requisite,
            currency_value: int,
            value: int,
            rate: int,
    ) -> Order:
        if order_type == OrderTypes.OUTPUT:
            await WalletBanService().create_related(
                wallet=request.wallet, value=value, reason=WalletBanReasons.BY_ORDER,
            )

        await RequisiteRepository().update(
            requisite,
            currency_value=round(requisite.currency_value - currency_value),
            value=round(requisite.value - value),
        )
        order = await OrderRepository().create(
            type=order_type,
            state=OrderStates.RESERVE,
            request=request,
            requisite=requisite,
            currency_value=currency_value,
            value=value,
            rate=rate,
            requisite_fields=requisite.requisite_data.fields,
        )

        return order

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        order = await OrderRepository().get_by_id(id_=id_)

        return {
            'requisite': {
                'id': order.id,
                'type': order.type,
                'state': order.state,
                'canceled_reason': order.canceled_reason,
                'request_id': order.request_id,
                'requisite_id': order.requisite_id,
                'wallet_ban_id': order.wallet_ban_id,
                'currency_value': order.currency_value,
                'value': order.value,
                'rate': order.rate,
                'requisite_fields': order.requisite_fields,
                'confirmation_fields': order.confirmation_fields,
            }
        }

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        order = await OrderRepository().get_by_id(id_=id_)
        await self.delete_related(order=order)
        await self.create_action(
            model=order,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )

        return {}

    async def delete_related(self, order: Order) -> None:
        await self.cancel_related(order=order)
        await OrderRepository().delete(order)

    @staticmethod
    async def cancel_related(order: Order) -> None:
        if order.type == OrderTypes.INPUT:
            await WalletBanService().create_related(
                wallet=order.request.wallet,
                value=-order.value,
                reason=WalletBanReasons.BY_ORDER,
            )
        await RequisiteRepository().update(
            order.requisite,
            currency_value=round(order.requisite.currency_value + order.currency_value),
            value=round(order.requisite.value + order.value),
        )

    @staticmethod
    async def compete_related(order: Order) -> None:
        if order.type == OrderTypes.INPUT:
            await WalletBanService().create_related(
                wallet=order.requisite.wallet,
                value=-order.value,
                reason=WalletBanReasons.BY_ORDER,
            )
            await TransferService().transfer(
                type_=TransferTypes.IN_ORDER,
                wallet_from=order.requisite.wallet,
                wallet_to=order.request.wallet,
                value=order.value,
            )
        elif order.type == OrderTypes.OUTPUT:  # FIXME (check)
            await WalletBanService().create_related(
                wallet=order.request.wallet,
                value=-order.value,
                reason=WalletBanReasons.BY_ORDER,
            )
            await TransferService().transfer(
                type_=TransferTypes.IN_ORDER,
                wallet_from=order.request.wallet,
                wallet_to=order.requisite.wallet,
                value=order.value,
            )
        await RequisiteRepository().update(
            order.requisite,
            currency_value=round(order.requisite.currency_value + order.currency_value),
            value=round(order.requisite.value + order.value),
        )
