import math


async def start_test():
    # request = await RequestRepository().get_by_id(id_=12)
    # await request_model_calculation(request=request)
    # for request in await RequestRepository().get_list(state=RequestStates.LOADING):
    #     if request.type == RequestTypes.ALL:  # ALL
    #         result = await request_type_all(request=request)
    #         if not result:
    #             continue
    #         for input_requisite_scheme in result.input_requisites:
    #             await OrderService().waited_order_by_scheme(
    #                 request=request, requisite_scheme=input_requisite_scheme, order_type=OrderTypes.INPUT,
    #             )
    #         for output_requisite_scheme in result.output_requisites:
    #             await OrderService().waited_order_by_scheme(
    #                 request=request, requisite_scheme=output_requisite_scheme, order_type=OrderTypes.OUTPUT,
    #             )
    #     elif request.type == RequestTypes.INPUT:  # INPUT
    #         result_list = await request_type_input(request=request)
    #         if not result_list:
    #             continue
    #         for requisite_scheme in result_list:
    #             await OrderService().waited_order_by_scheme(
    #                 request=request, requisite_scheme=requisite_scheme, order_type=OrderTypes.INPUT,
    #             )
    #     elif request.type == RequestTypes.OUTPUT:  # OUTPUT
    #         result_list = await request_type_output(request=request)
    #         if not result_list:
    #             continue
    #         for requisite_scheme in result_list:
    #             await OrderService().waited_order_by_scheme(
    #                 request=request, requisite_scheme=requisite_scheme, order_type=OrderTypes.OUTPUT,
    #             )
    #     await request_model_calculation(request=request)
    return


if __name__ == '__main__':
    c_percent = 100
    c_value = 200

    value1 = 10000
    c_1 = math.ceil(value1 - value1 * (100_00 - c_percent) / 100_00)
    c_1 += c_value
    result1 = value1 - c_1
    print(value1, '->', c_1, '->', result1)
    value2 = result1
    c_value_2 = value2 + c_value
    c_2 = math.ceil(c_value_2 / (100_00 - c_percent) * 100_00 - c_value_2)
    c_2 += c_value
    result2 = value2 + c_2

    print(value2, '->', c_2, '->', result2)
