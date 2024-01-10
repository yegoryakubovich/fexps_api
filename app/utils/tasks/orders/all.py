from app.db.models import Request


async def create_orders_all(request: Request) -> None:
    print('request.input_method', request.input_method)
    print('request.input_value', request.input_value)
    print('request.output_requisite_data_id', request.output_requisite_data_id)
    print('request.output_value', request.output_value)
    print('request.value', request.value)
