from app.db.models import Request, RequestTypes, OrderTypes, OrderStates
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.utils.calculations.request.divs import get_div_auto
from app.utils.calculations.request.rates import get_auto_rate


async def write_other(
        request: Request,
        check_rate_confirmed: bool = True,
) -> None:
    if check_rate_confirmed and request.rate_confirmed:
        return
    data = {}
    if request.type == RequestTypes.INPUT:
        data = await get_input_data(request=request)
        data.update(rate=data['input_rate'])
    elif request.type == RequestTypes.OUTPUT:
        data = await get_output_data(request=request)
        data.update(rate=data['output_rate'])
    elif request.type == RequestTypes.ALL:
        data = await get_all_data(request=request)
    data['div_value'] = await get_div_auto(request=request)
    await RequestRepository().update(request, **data)


async def get_input_data(
        request: Request,
) -> dict:
    _currency_value, _value, _rate = 0, 0, 0
    for order in await OrderRepository().get_list(request=request, type=OrderTypes.INPUT):
        if order.state == OrderStates.CANCELED:
            continue
        _currency_value = round(_currency_value + order.currency_value)
        _value = round(_value + order.value)
    if _value <= 0:
        return {'input_currency_value': _currency_value, 'input_value': _value, 'input_rate': _rate}
    _value = round(_value - request.commission_value)
    _rate = get_auto_rate(
        request=request,
        currency_value=_currency_value,
        value=_value,
        rate_decimal=request.rate_decimal,
    )
    return {'input_currency_value': _currency_value, 'input_value': _value, 'input_rate': _rate}


async def get_output_data(
        request: Request,
) -> dict:
    _currency_value, _value, _rate = 0, 0, 0
    for order in await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT):
        if order.state == OrderStates.CANCELED:
            continue
        _currency_value = round(_currency_value + order.currency_value)
        _value = round(_value + order.value)
    if _value <= 0:
        return {'output_currency_value': _currency_value, 'output_value': _value, 'output_rate': _rate}
    _rate = get_auto_rate(
        request=request,
        currency_value=_currency_value,
        value=_value,
        rate_decimal=request.rate_decimal,
    )
    return {'output_currency_value': _currency_value, 'output_value': _value, 'output_rate': _rate}


async def get_all_data(
        request: Request,
) -> dict:
    data = {}
    input_data = await get_input_data(request=request)
    output_data = await get_output_data(request=request)
    _output_currency_value = request.output_currency_value_raw
    if output_data.get('output_currency_value'):
        _output_currency_value = output_data.get('output_currency_value')
    rate = get_auto_rate(
        request=request,
        currency_value=input_data['input_currency_value'],
        value=_output_currency_value,
        rate_decimal=request.rate_decimal,
    )
    data.update(input_data)
    data.update(output_data)
    data.update(rate=rate)
    return data
