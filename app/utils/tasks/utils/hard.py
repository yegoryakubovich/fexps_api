from typing import Optional

from app.db.models import Request, OrderStates
from app.repositories.order import OrderRepository


async def get_need_values_input(request: Request, order_type: str) -> tuple[Optional[int], Optional[int]]:
    result_currency_value, result_value = request.input_currency_value, request.input_value
    for order in await OrderRepository().get_list(request=request, type=order_type):
        if order.state == OrderStates.CANCELED:
            continue
        if request.input_currency_value:
            result_currency_value = round(result_currency_value - order.currency_value)
        if request.input_value:
            result_value = round(result_value - order.value)
    print(f'result_currency_value: {request.input_currency_value} -> {result_currency_value}')
    print(f'result_value: {request.input_value} -> {result_value}')
    return result_currency_value, result_value


async def get_need_values_output(request: Request, order_type: str) -> tuple[Optional[int], Optional[int]]:
    result_currency_value, result_value = request.output_currency_value, request.output_value
    for order in await OrderRepository().get_list(request=request, type=order_type):
        if order.state == OrderStates.CANCELED:
            continue
        if request.output_currency_value:
            result_currency_value = round(result_currency_value - order.currency_value)
        if request.output_value:
            result_value = round(result_value - order.value)
    print(f'result_currency_value: {request.output_currency_value} -> {result_currency_value}')
    print(f'result_value: {request.output_value} -> {result_value}')
    return result_currency_value, result_value
