import logging
from typing import List

from app.db.models import OrderTypes, Request, Currency, RequisiteTypes, RequestFirstLine
from app.repositories.requisite import RequisiteRepository
from app.utils.calculations.request.need_value import output_get_need_currency_value, output_get_need_value
from app.utils.calculations.schemes.loading import RequisiteScheme, RequisiteTypeScheme
from app.utils.calculations.simples import get_div_by_value, get_div_by_currency_value

prefix = '[request_type_output]'


async def request_type_output(
        request: Request,
) -> RequisiteTypeScheme:
    currency = request.output_method.currency
    logging.info(f'{prefix} req_{request.id} first_line={request.first_line}, currency={currency.id_str}')
    if request.first_line == RequestFirstLine.OUTPUT_CURRENCY_VALUE:
        need_currency_value = await output_get_need_currency_value(request=request)
        logging.info(f'req_{request.id} зашел в OUTPUT_CURRENCY_VALUE, need_currency_value={need_currency_value}')
        return await request_type_output_currency_value(
            request=request,
            currency=currency,
            need_currency_value=need_currency_value,
        )
    elif request.first_line == RequestFirstLine.OUTPUT_VALUE:
        need_value = await output_get_need_value(request=request)
        logging.info(f'req_{request.id} зашел в OUTPUT_VALUE, need_value={need_value}')
        return await request_type_output_value(
            request=request,
            currency=currency,
            need_value=need_value,
        )


async def request_type_output_currency_value(
        request: Request,
        currency: Currency,
        need_currency_value: int,
) -> RequisiteTypeScheme:
    requisites_scheme_list: List[RequisiteScheme] = []
    sum_currency_value, sum_value = 0, 0
    for requisite in await RequisiteRepository().get_list_output_by_rate(
            type=RequisiteTypes.INPUT,
            currency=currency,
            in_process=False,
    ):
        await RequisiteRepository().update(requisite, in_process=True)
        rate_decimal, requisite_rate_decimal = request.rate_decimal, requisite.currency.rate_decimal
        requisite_rate = requisite.rate
        if rate_decimal != requisite_rate_decimal:
            requisite_rate = round(requisite.rate / 10 ** requisite_rate_decimal * 10 ** rate_decimal)
        _need_currency_value = need_currency_value
        # Zero check
        if 0 in [_need_currency_value, requisite.currency_value]:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        # Min/Max check
        if requisite.currency_value_min and _need_currency_value < requisite.currency_value_min:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        if requisite.currency_value_max and _need_currency_value > requisite.currency_value_max:
            _need_currency_value = requisite.currency_value_max
        # Div check
        if _need_currency_value < currency.div:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        # Check max possible value
        if requisite.currency_value >= _need_currency_value:
            suitable_currency_value = _need_currency_value
        else:
            suitable_currency_value = requisite.currency_value
        # Check TRUE
        suitable_currency_value, suitable_value = get_div_by_currency_value(  # Rounded value
            currency_value=suitable_currency_value,
            div=currency.div,
            rate=requisite_rate,
            rate_decimal=rate_decimal,
            order_type=OrderTypes.OUTPUT,
        )
        requisites_scheme_list.append(RequisiteScheme(  # Add to list
            requisite_id=requisite.id,
            currency_value=suitable_currency_value,
            value=suitable_value,
            rate=requisite_rate,
        ))
        # Write summary
        sum_currency_value = round(sum_currency_value + suitable_currency_value)
        sum_value = round(sum_value + suitable_value)
        # Edit need_value
        need_currency_value = round(need_currency_value - suitable_currency_value)
    if not requisites_scheme_list:
        return
    if need_currency_value >= currency.div:  # Check complement
        for requisite_scheme in requisites_scheme_list:
            requisite = await RequisiteRepository().get_by_id(id_=requisite_scheme.requisite_id)
            await RequisiteRepository().update(requisite, in_process=False)
        return
    # Return result
    return RequisiteTypeScheme(
        requisites_scheme_list=requisites_scheme_list,
        sum_currency_value=sum_currency_value,
        sum_value=sum_value,
    )


async def request_type_output_value(
        request: Request,
        currency: Currency,
        need_value: int,
) -> RequisiteTypeScheme:
    requisites_scheme_list: List[RequisiteScheme] = []
    sum_currency_value, sum_value, rates_list = 0, 0, []
    for requisite in await RequisiteRepository().get_list_output_by_rate(
            type=RequisiteTypes.INPUT,
            currency=currency,
            in_process=False,
    ):
        await RequisiteRepository().update(requisite, in_process=True)
        rate_decimal, requisite_rate_decimal = request.rate_decimal, requisite.currency.rate_decimal
        requisite_rate = requisite.rate
        if rate_decimal != requisite_rate_decimal:
            requisite_rate = round(requisite.rate / 10 ** requisite_rate_decimal * 10 ** rate_decimal)
        _need_value = need_value
        # Zero check
        if 0 in [_need_value, requisite.value]:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        # Min/Max check
        if requisite.value_min and _need_value < requisite.value_min:  # Меньше минимума
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        if requisite.value_max and _need_value > requisite.value_max:  # Больше максимума
            _need_value = requisite.value_max
        # Div check
        if round(_need_value * requisite_rate / 10 ** rate_decimal) < currency.div:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        # Check max possible value
        if requisite.value >= _need_value:
            suitable_value = _need_value
        else:
            suitable_value = requisite.value
        # Check TRUE
        suitable_currency_value, suitable_value = get_div_by_value(
            value=suitable_value,
            div=currency.div,
            rate=requisite_rate,
            rate_decimal=rate_decimal,
            type_=OrderTypes.OUTPUT,
        )
        requisites_scheme_list.append(RequisiteScheme(  # Add to list
            requisite_id=requisite.id,
            currency_value=suitable_currency_value,
            value=suitable_value,
            rate=requisite_rate,
        ))
        # Write summary and rate
        sum_currency_value = round(sum_currency_value + suitable_currency_value)
        sum_value = round(sum_value + suitable_value)
        rates_list.append(requisite_rate)
        # Edit need_value
        need_value = round(need_value - suitable_value)
    if not requisites_scheme_list:
        return
    mean_rate = round(sum(rates_list) / len(rates_list))
    need_currency_value = round(need_value * mean_rate / 10 ** request.rate_decimal)
    if need_currency_value >= currency.div:  # Check complement
        for requisite_scheme in requisites_scheme_list:
            requisite = await RequisiteRepository().get_by_id(id_=requisite_scheme.requisite_id)
            await RequisiteRepository().update(requisite, in_process=False)
        return
    # Return result
    return RequisiteTypeScheme(
        requisites_scheme_list=requisites_scheme_list,
        sum_currency_value=sum_currency_value,
        sum_value=sum_value,
    )
