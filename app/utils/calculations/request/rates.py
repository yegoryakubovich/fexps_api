import math

from app.db.models import Request, RequestTypes, RequestFirstLine


def get_rate_by_input(
        currency_value: int,
        value: int,
        rate_decimal: int,
) -> int:
    return math.ceil(currency_value / value * (10 ** rate_decimal))


def get_rate_by_output(
        currency_value: int,
        value: int,
        rate_decimal: int,
) -> int:
    return math.floor(currency_value / value * (10 ** rate_decimal))


def get_auto_rate(
        request: Request,
        currency_value: int,
        value: int,
        rate_decimal: int,
) -> int:
    if request.type == RequestTypes.ALL and request.first_line in RequestFirstLine.choices_output:
        return get_rate_by_input(
            currency_value=currency_value,
            value=value,
            rate_decimal=rate_decimal,
        )
    return get_rate_by_input(
        currency_value=currency_value,
        value=value,
        rate_decimal=rate_decimal,
    )
