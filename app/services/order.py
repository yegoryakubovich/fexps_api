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


from app.db.models import Session, Order, Actions, Requisite, OrderTypes, Request, WalletBanReasons, OrderStates
from app.repositories.order import OrderRepository
from app.repositories.requisite import RequisiteRepository
from app.services.base import BaseService
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
        wallet_ban = None
        if order_type == OrderTypes.OUTPUT:
            wallet_ban = await WalletBanService().create_related(
                wallet=request.wallet,
                value=value,
                reason=WalletBanReasons.BY_ORDER,
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
            wallet_ban=wallet_ban,
            currency_value=currency_value,
            value=value,
            rate=rate,
        )

        return order

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
        await self.canceled_related(order=order)
        await OrderRepository().delete(order)

    @staticmethod
    async def canceled_related(order: Order) -> None:
        if order.wallet_ban:
            await WalletBanService().delete_related(wallet_ban=order.wallet_ban)
        await RequisiteRepository().update(
            order.requisite,
            currency_value=round(order.requisite.currency_value + order.currency_value),
            value=round(order.requisite.value + order.value),
        )
