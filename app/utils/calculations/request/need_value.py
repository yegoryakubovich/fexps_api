from app.db.models import Request, OrderStates, OrderTypes
from app.repositories.order import OrderRepository


async def check_need_value(
        request: Request,
        order_type: str,
        from_value: int,
) -> int:
    result = from_value
    for order in await OrderRepository().get_list(request=request, type=order_type):
        if order.state == OrderStates.CANCELED:
            continue
        result = round(result - order.value)
    return result


# INPUT
async def input_get_need_currency_value(request: Request, from_value: int = None) -> int:
    result = from_value if from_value else request.first_line_value
    for order in await OrderRepository().get_list(request=request, type=OrderTypes.INPUT):
        if order.state == OrderStates.CANCELED:
            continue
        result = round(result - order.currency_value)
    return result


async def input_get_need_value(request: Request, from_value: int = None) -> int:
    result = from_value if from_value else request.first_line_value
    for order in await OrderRepository().get_list(request=request, type=OrderTypes.INPUT):
        if order.state == OrderStates.CANCELED:
            continue
        result = round(result - order.value)
    return result


# OUTPUT
async def output_get_need_currency_value(request: Request, from_value: int = None) -> int:
    result = from_value if from_value else request.first_line_value
    for order in await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT):
        if order.state == OrderStates.CANCELED:
            continue
        result = round(result - order.currency_value)
    return result


async def output_get_need_value(request: Request, from_value: int = None) -> int:
    result = from_value if from_value else request.first_line_value
    for order in await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT):
        if order.state == OrderStates.CANCELED:
            continue
        result = round(result - order.value)
    return result
