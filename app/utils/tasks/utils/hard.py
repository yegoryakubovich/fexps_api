from app.db.models import Request, OrderStates
from app.repositories.order import OrderRepository


async def get_need_values_by_request(request: Request, order_type: str) -> tuple[int, int]:
    result_input_value, result_value = request.input_value, request.value
    for order in await OrderRepository().get_list(request=request, type=order_type):
        if order.state == OrderStates.CANCELED:
            continue
        if request.input_value:
            result_input_value = round(result_input_value - order.currency_value)
        elif request.value:
            result_value = round(result_value - order.currency_value)
    return result_input_value, result_value
