from app.db.models import Request, Currency
from app.utils.custom_calc import round_ceil
from .input import calc_input_value2currency, calc_input_currency2value
from .output import calc_output_value2currency, calc_output_currency2value


async def create_orders(request: Request):
    pass
    # if request.type == RequestTypes.INPUT:
    #     asyncio.create_task(create_orders_input(request=request), name=f"CREATE_ORDER_INPUT_{request.id}")
    # elif request.type == RequestTypes.OUTPUT:
    #     asyncio.create_task(create_orders_output(request=request), name=f"CREATE_ORDER_OUTPUT_{request.id}")
    # elif request.type == RequestTypes.ALL:
    #     asyncio.create_task(create_orders_input(request=request), name=f"CREATE_ORDER_ALL_INPUT_{request.id}")
    #     asyncio.create_task(create_orders_output(request=request), name=f"CREATE_ORDER_ALL_OUTPUT_{request.id}")


async def calc_all(
        currency_input: Currency,
        currency_output: Currency,
        currency_value_input: float = None,
        currency_value_output: float = None,
) -> dict:
    if currency_value_input:
        calc_input = await calc_input_currency2value(currency=currency_input, currency_value=currency_value_input)
        print(calc_input)
        calc_output = await calc_output_value2currency(currency=currency_output, value=calc_input['value'])
        print(calc_output)
        rate_fix = round_ceil(calc_input['currency_value'] / calc_output['currency_value'])
        return {
            'calc_input': calc_input,
            'calc_output': calc_output,
            'currency_value_input': calc_input['currency_value'],
            'currency_value_output': calc_output['currency_value'],
            'rate': rate_fix,
        }
    elif currency_value_output:
        calc_output = await calc_output_currency2value(currency=currency_output, currency_value=currency_value_output)
        print(calc_output)
        calc_input = await calc_input_value2currency(currency=currency_input, value=calc_output['value'])
        print(calc_input)
        rate_fix = round_ceil(calc_input['currency_value'] / calc_output['currency_value'])
        return {
            'calc_output': calc_input,
            'calc_input': calc_output,
            'currency_value_input': calc_input['currency_value'],
            'currency_value_output': calc_output['currency_value'],
            'rate': rate_fix,
        }
