from app.db.models import Request


async def create_orders_output(request: Request) -> None:
    print('request.output_method_id', request.output_method_id)
    print('request.output_requisite_data_id', request.output_requisite_data_id)
    print('request.output_value', request.output_value)
    print('request.value', request.value)
