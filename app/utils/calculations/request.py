import math
from typing import List

from app.db.models import Request, OrderTypes, RequestTypes, OrderStates
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.utils.calculations.hard import get_commission
from app.utils.schemes.calculations.orders import RequisiteScheme


async def request_model_calculation(request: Request):
    if request.rate_confirmed:
        return
    data = {}
    if request.type == RequestTypes.INPUT:
        data = await data_input_calc(request=request)
    elif request.type == RequestTypes.OUTPUT:
        data = await data_output_calc(request=request)
    elif request.type == RequestTypes.ALL:
        data = await data_all_calc(request=request)
    await RequestRepository().update(request, **data)


async def data_all_calc(request: Request) -> dict:
    data = {}
    input_data = await data_input_calc(request=request)
    output_data = await data_output_calc(request=request)

    rate = math.ceil(
        input_data['input_currency_value'] / output_data['output_currency_value'] * 10 ** request.rate_decimal
    ) if output_data['output_currency_value'] > 0 else 0
    data.update(input_data)
    data.update(output_data)
    data.update(rate=rate)
    return data


async def data_input_calc(request: Request) -> dict:
    result = {
        'input_currency_value': 0,
        'input_value': 0,
        'input_rate': 0,
        'rate': 0,
        'commission_value': 0,
    }
    for order in await OrderRepository().get_list(request=request, type=OrderTypes.INPUT):
        if order.state == OrderStates.CANCELED:
            continue
        result['input_currency_value'] = round(result['input_currency_value'] + order.currency_value)
        result['input_value'] = round(result['input_value'] + order.value)
    if result['input_value'] <= 0:
        return result
    result['commission_value'] = await get_commission(wallet_id=request.wallet_id, value=result['input_value'])
    result['input_value'] = round(result['input_value'] - result['commission_value'])
    rate = math.ceil(result['input_currency_value'] / result['input_value'] * 10 ** request.rate_decimal)
    result['rate'] = result['input_rate'] = rate
    return result


async def data_output_calc(request: Request) -> dict:
    result = {
        'output_currency_value': 0,
        'output_value': 0,
        'output_rate': 0,
        'rate': 0,
        'div_value': 0,
    }
    for order in await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT):
        if order.state == OrderStates.CANCELED:
            continue
        result['output_currency_value'] = round(result['output_currency_value'] + order.currency_value)
        result['output_value'] = round(result['output_value'] + order.value)
    if result['output_value'] <= 0:
        return result
    rate = math.ceil(result['output_currency_value'] / result['output_value'] * 10 ** request.rate_decimal)
    result['rate'] = result['output_rate'] = rate
    if request.input_value:
        need_value = round(request.input_value - result['output_value'])
        if need_value < request.output_method.currency.div:
            result['div_value'] = need_value
    elif request.output_value:
        need_value = round(request.output_value - result['output_value'])
        if need_value < request.output_method.currency.div:
            result['div_value'] = need_value
    elif request.output_currency_value:
        _value = round(request.output_currency_value / result['rate'] * 10 ** request.rate_decimal)
        need_value = round(_value - result['output_value'])
        if need_value < request.output_method.currency.div:
            result['div_value'] = need_value
    return result


async def calc_request_value(request: Request, requisites_list: List[RequisiteScheme], type_: str) -> tuple[int, int]:
    currency_value, value = 0, 0
    for requisite in requisites_list:
        currency_value = round(currency_value + requisite.currency_value)
        value = round(value + requisite.value)
    if type_ == 'input':
        value = round(value - await get_commission(wallet_id=request.wallet_id, value=value))
    return currency_value, value
