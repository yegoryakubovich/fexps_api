import math

from app.db.models import Request, RequestTypes, RequestFirstLine
from app.utils.calculations.request.need_value import output_get_need_currency_value, output_get_need_value, \
    input_get_need_value


async def get_div_all(request: Request) -> int:
    result = 0
    if request.first_line == RequestFirstLine.INPUT_CURRENCY_VALUE:
        currency = request.output_method.currency
        _rate = request.output_rate if request.output_rate else request.output_rate_raw
        if not _rate:
            return result
        _from_value = request.input_value_raw - request.commission_value
        if request.input_value:
            _from_value = request.input_value
        _need_currency_value = await output_get_need_value(request=request, from_value=_from_value)
        _need_value = math.floor(_need_currency_value / _rate * 10 ** request.rate_decimal)
        if _need_currency_value < currency.div:
            result = _need_value
    elif request.first_line == RequestFirstLine.OUTPUT_CURRENCY_VALUE:
        currency = request.input_method.currency
        _rate = request.input_rate if request.input_rate else request.input_rate_raw
        if not _rate:
            return result
        _from_value = request.input_value_raw
        if request.input_value:
            _from_value = request.input_value + request.commission_value
        _need_currency_value = await input_get_need_value(request=request, from_value=_from_value)
        _need_value = math.ceil(_need_currency_value / _rate * 10 ** request.rate_decimal)
        if _need_currency_value < currency.div:
            result = _need_value
    return result


async def get_div_output(request: Request) -> int:
    result = 0
    currency = request.output_method.currency
    _rate = request.output_rate if request.output_rate else request.output_rate_raw
    if not _rate:
        return result
    if request.first_line == RequestFirstLine.OUTPUT_CURRENCY_VALUE:
        _need_currency_value = await output_get_need_currency_value(request=request)
        _need_value = math.floor(_need_currency_value / _rate * 10 ** request.rate_decimal)
        if _need_currency_value < currency.div:
            result = _need_value
    elif request.first_line == RequestFirstLine.OUTPUT_VALUE:
        _need_value = await output_get_need_value(request=request)
        _need_currency_value = round(_need_value * _rate / 10 ** request.rate_decimal)
        if _need_currency_value < currency.div:
            result = _need_value
    return result


async def get_div_auto(request: Request) -> int:
    if request.type == RequestTypes.ALL:
        return await get_div_all(request=request)
    elif request.type == RequestTypes.OUTPUT:
        return await get_div_output(request=request)
    return 0
