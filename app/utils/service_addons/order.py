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


from app.db.models import Request, OrderTypes, OrderStates, Order, Requisite, WalletBanReasons, Wallet, TransferTypes
from app.repositories.order import OrderRepository
from app.repositories.requisite import RequisiteRepository
from app.services.wallet_ban import WalletBanService
from app.utils.calculations.schemes.loading import RequisiteScheme
from app.utils.service_addons.transfer import create_transfer


async def order_banned_value(
        wallet: Wallet,
        value: int,
        ignore_bal: bool = False,
) -> None:
    await WalletBanService().create_related(
        wallet=wallet,
        value=value,
        reason=WalletBanReasons.BY_ORDER,
        ignore_bal=ignore_bal,
    )


async def waited_order(
        request: Request,
        requisite: Requisite,
        currency_value: int,
        value: int,
        rate: int,
        order_type: str,
        order_state: str = OrderStates.WAITING,
) -> Order:
    await RequisiteRepository().update(
        requisite,
        currency_value=round(requisite.currency_value - currency_value),
        value=round(requisite.value - value),
        in_process=False,
    )
    return await OrderRepository().create(
        type=order_type,
        state=order_state,
        request=request,
        requisite=requisite,
        currency_value=currency_value,
        value=value,
        rate=rate,
        requisite_fields=requisite.output_requisite_data.fields if requisite.output_requisite_data else None,
    )


async def waited_order_by_scheme(
        request: Request,
        requisite_scheme: RequisiteScheme,
        order_type: str,
        order_state: str = OrderStates.WAITING,
) -> None:
    requisite = await RequisiteRepository().get_by_id(id_=requisite_scheme.requisite_id)
    await waited_order(
        request=request,
        requisite=requisite,
        currency_value=requisite_scheme.currency_value,
        value=requisite_scheme.value,
        rate=requisite_scheme.rate,
        order_type=order_type,
        order_state=order_state,
    )


async def order_cancel_related(order: Order) -> None:
    if order.type == OrderTypes.OUTPUT and order.state in OrderStates.choices_return_banned_value:
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


async def order_compete_related(order: Order) -> None:
    if order.type == OrderTypes.INPUT:
        await WalletBanService().create_related(
            wallet=order.requisite.wallet,
            value=-order.value,
            reason=WalletBanReasons.BY_ORDER,
        )
        await create_transfer(
            type_=TransferTypes.IN_ORDER,
            wallet_from=order.requisite.wallet,
            wallet_to=order.request.wallet,
            value=order.value,
            order=order,
        )
        await WalletBanService().create_related(
            wallet=order.request.wallet,
            value=order.value,
            reason=WalletBanReasons.BY_ORDER,
        )
    elif order.type == OrderTypes.OUTPUT:
        await WalletBanService().create_related(
            wallet=order.request.wallet,
            value=-order.value,
            reason=WalletBanReasons.BY_ORDER,
        )
        await create_transfer(
            type_=TransferTypes.IN_ORDER,
            wallet_from=order.request.wallet,
            wallet_to=order.requisite.wallet,
            value=order.value,
            order=order,
        )
