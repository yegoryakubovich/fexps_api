from typing import List

from app.db.models import Request, RequisiteTypes, Requisite, OrderTypes
from app.db.models.order import OrderStates
from app.repositories.order import OrderRepository
from app.repositories.requisite import RequisiteRepository
from app.services import RequestService


async def create_orders_input(request: Request) -> None:
    input_requisites: List[Requisite] = await RequisiteRepository().get_list_order_by_rate(
        type=RequisiteTypes.INPUT, currency=request.input_method.currency
    )
    for input_requisite in input_requisites:
        if request.value:
            need_value = await RequestService().get_need_value(request=request, value=request.value)
            if not need_value:
                continue

            if input_requisite.value >= need_value:
                suitable_value = need_value
            else:
                suitable_value = input_requisite.value
            if not suitable_value:
                continue
            input_requisite_value = input_requisite.value - suitable_value
            input_requisite_currency_value = input_requisite_value * input_requisite.rate
            await RequisiteRepository().update(
                input_requisite,
                currency_value=input_requisite_currency_value, value=input_requisite_value
            )
            await OrderRepository().create(
                request=request,
                requisite=input_requisite,
                type=OrderTypes.INPUT,
                state=OrderStates.RESERVE,
                currency_value=suitable_value * input_requisite.rate,
                value=suitable_value,
                rate=input_requisite.rate
            )
        else:
            need_value = await RequestService().get_need_value(request=request, input_value=request.input_value)
            if not need_value:
                continue
            if input_requisite.currency_value >= need_value:
                suitable_value = need_value
            else:
                suitable_value = input_requisite.currency_value
            if not suitable_value:
                continue
            input_requisite_currency_value = input_requisite.currency_value - suitable_value
            input_requisite_value = input_requisite_currency_value / input_requisite.rate
            await RequisiteRepository().update(
                input_requisite,
                currency_value=input_requisite_currency_value, value=input_requisite_value
            )
            await OrderRepository().create(
                request=request,
                requisite=input_requisite,
                type=OrderTypes.INPUT,
                state=OrderStates.RESERVE,
                currency_value=suitable_value,
                value=suitable_value / input_requisite.rate,
                rate=input_requisite.rate
            )
