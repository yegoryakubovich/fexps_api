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


import math

from app.db.models import Request, OrderTypes, OrderStates, Order, Requisite, WalletBanReasons, Wallet, TransferTypes, \
    RequestRequisiteTypes
from app.repositories import RequestRepository, RequestRequisiteRepository
from app.repositories.order import OrderRepository
from app.repositories.requisite import RequisiteRepository
from app.services.wallet_ban import WalletBanService
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
    requisite_scheme_fields, requisite_fields, input_scheme_fields, input_fields = None, None, None, None
    if order_type == OrderTypes.INPUT:
        requisite_scheme_fields = requisite.output_requisite_data.method.schema_fields
        requisite_fields = requisite.output_requisite_data.fields
        input_scheme_fields = requisite.output_requisite_data.method.schema_input_fields
    elif order_type == OrderTypes.OUTPUT:
        requisite_scheme_fields = request.output_requisite_data.method.schema_fields
        requisite_fields = request.output_requisite_data.fields
        input_scheme_fields = request.output_requisite_data.method.schema_input_fields
    return await OrderRepository().create(
        type=order_type,
        state=order_state,
        request=request,
        requisite=requisite,
        currency_value=currency_value,
        value=value,
        rate=rate,
        requisite_scheme_fields=requisite_scheme_fields,
        requisite_fields=requisite_fields,
        input_scheme_fields=input_scheme_fields,
        input_fields=input_fields,
    )


async def order_cancel_related(order: Order) -> None:
    request = order.request
    if order.type == OrderTypes.INPUT:
        current_currency_value = request.input_currency_value - order.currency_value
        current_value = request.input_value - order.value
        current_commission = math.ceil(request.commission / request.input_currency_value * current_currency_value)
        await RequestRepository().update(
            request,
            commission=current_commission,
            input_currency_value=current_currency_value,
            input_value=current_value,
        )
    elif order.type == OrderTypes.OUTPUT:
        await RequestRepository().update(
            request,
            output_currency_value=request.output_currency_value - order.currency_value,
            output_value=request.output_value - order.value,
        )
        if order.state in [OrderStates.PAYMENT, OrderStates.CONFIRMATION]:
            await WalletBanService().create_related(
                wallet=request.wallet,
                value=-order.value,
                reason=WalletBanReasons.BY_ORDER,
            )
    await RequisiteRepository().update(
        order.requisite,
        currency_value=round(order.requisite.currency_value + order.currency_value),
        value=round(order.requisite.value + order.value),
    )


async def order_recreate_related(order: Order) -> None:
    await RequestRequisiteRepository().create(
        request=order.request,
        requisite=order.requisite,
        type=RequestRequisiteTypes.BLACKLIST,
    )
    if order.type == OrderTypes.OUTPUT:
        if order.state in [OrderStates.PAYMENT, OrderStates.CONFIRMATION]:
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


async def order_edit_value_related(
        order: Order,
        delta_value: int,
        delta_currency_value: int,
) -> None:
    request = order.request
    if order.type == OrderTypes.INPUT:
        current_currency_value = request.input_currency_value - delta_currency_value
        current_value = request.input_value - delta_value
        current_commission = math.ceil(request.commission / request.input_currency_value * current_currency_value)
        await RequestRepository().update(
            request,
            commission=current_commission,
            input_currency_value=current_currency_value,
            input_value=current_value,
        )
    elif order.type == OrderTypes.OUTPUT:
        await RequestRepository().update(
            request,
            output_currency_value=request.output_currency_value - delta_currency_value,
            output_value=request.output_value - delta_value,
        )
        if order.state in [OrderStates.PAYMENT, OrderStates.CONFIRMATION]:
            await WalletBanService().create_related(
                wallet=request.wallet,
                value=-delta_value,
                reason=WalletBanReasons.BY_ORDER,
            )
    await RequisiteRepository().update(
        order.requisite,
        currency_value=round(order.requisite.currency_value + delta_currency_value),
        value=round(order.requisite.value + delta_value),
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
