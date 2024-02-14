import math

from app.db.models import RequisiteTypes


async def all_value_calc(
        type_: RequisiteTypes, rate_decimal: int, currency_value: int, value: int, rate: int,
) -> tuple[int, int, int]:
    rate_currency_value_method = math.ceil if type_ == RequisiteTypes.OUTPUT else math.floor
    value_method = math.floor if type_ == RequisiteTypes.OUTPUT else math.ceil
    if currency_value and value:
        rate = rate_currency_value_method(currency_value / value * 10 ** rate_decimal)
    elif currency_value and rate:
        value = value_method(currency_value / rate * 10 ** rate_decimal)
    else:
        currency_value = rate_currency_value_method(value * rate / 10 ** rate_decimal)
    return currency_value, value, rate
