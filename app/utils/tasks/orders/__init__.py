from app.db.models import Request, RequestTypes
from .all import create_orders_all
from .input import create_orders_input
from .output import create_orders_output


async def create_orders(request: Request):
    if request.type == RequestTypes.INPUT:
        await create_orders_input(request=request)
    if request.type == RequestTypes.OUTPUT:
        await create_orders_output(request=request)
    if request.type == RequestTypes.ALL:
        await create_orders_all(request=request)

    # await OrderRepository().create(
    #     request=request
    # )
