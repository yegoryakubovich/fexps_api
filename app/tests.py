import redis


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
    redis = redis.Redis(
        host='37.1.192.150',
        port=2001,
        username='default',
        password='YKrcAH1X130PqxlheNJzpMZC3pupGwZQPXpya0R8Wj1O3iuZSMVNhOTdHVvXFH9f',
        decode_responses=True,
    )
    print(type(redis.keys()))
    redis.delete(*redis.keys())
    print(redis.keys())


