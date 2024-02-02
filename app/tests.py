from app.db.models import RequestStates, RequestTypes, OrderTypes, Actions
from app.repositories.request import RequestRepository
from app.services import OrderService
from app.services.base import BaseService
from app.tasks.schedule.requests.states.loading import request_type_all, request_type_input, request_type_output
from app.utils.calculations.request import request_model_calculation


async def start_test():
    for request in await RequestRepository().get_list(state=RequestStates.LOADING):
        if request.type == RequestTypes.ALL:  # ALL
            result = await request_type_all(request=request)
            if not result:
                continue
            for input_requisite_scheme in result.input_requisites:
                await OrderService().waited_order_by_scheme(
                    request=request, requisite_scheme=input_requisite_scheme, order_type=OrderTypes.INPUT,
                )
            for output_requisite_scheme in result.output_requisites:
                await OrderService().waited_order_by_scheme(
                    request=request, requisite_scheme=output_requisite_scheme, order_type=OrderTypes.OUTPUT,
                )
        elif request.type == RequestTypes.INPUT:  # INPUT
            result_list = await request_type_input(request=request)
            if not result_list:
                continue
            for requisite_scheme in result_list:
                await OrderService().waited_order_by_scheme(
                    request=request, requisite_scheme=requisite_scheme, order_type=OrderTypes.INPUT,
                )
        elif request.type == RequestTypes.OUTPUT:  # OUTPUT
            result_list = await request_type_output(request=request)
            if not result_list:
                continue
            for requisite_scheme in result_list:
                await OrderService().waited_order_by_scheme(
                    request=request, requisite_scheme=requisite_scheme, order_type=OrderTypes.OUTPUT,
                )
        await request_model_calculation(request=request)
