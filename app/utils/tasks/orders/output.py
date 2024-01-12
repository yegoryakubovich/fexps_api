from app.db.models import Currency, RequisiteTypes
from app.repositories.requisite import RequisiteRepository
from app.utils.custom_calc import minus, round_floor, round_ceil, plus


async def calc_output_currency2value(
        currency: Currency,
        currency_value: float,
) -> dict:
    selected_requisites = []
    for requisite in await RequisiteRepository().get_list_output_by_rate(
            type=RequisiteTypes.OUTPUT, currency=currency,
    ):
        if 0 in [currency_value, requisite.currency_value]:
            continue
        if requisite.currency_value >= currency_value:
            suitable_currency_value = currency_value
        else:
            suitable_currency_value = requisite.currency_value
        suitable_value = round_ceil(number=suitable_currency_value / requisite.rate)
        print(suitable_value)
        selected_requisites.append({
            'requisite_id': requisite.id,
            'currency_value': suitable_currency_value,
            'value': suitable_value,
            'rate': requisite.rate,
        })
        currency_value = minus(currency_value, suitable_currency_value)
    currency_value_fix = 0
    value_fix = 0
    for select_requisite in selected_requisites:
        currency_value_fix = plus(currency_value_fix, select_requisite.get('currency_value'))
        value_fix = plus(value_fix, select_requisite.get('value'))
    rate_fix = round_floor(currency_value_fix / value_fix)
    return {
        'selected_requisites': selected_requisites,
        'currency_value': currency_value_fix,
        'value': value_fix,
        'rate_fix': rate_fix,
    }


async def calc_output_value2currency(
        currency: Currency,
        value: float,
) -> dict:
    selected_requisites = []
    for requisite in await RequisiteRepository().get_list_output_by_rate(
            type=RequisiteTypes.OUTPUT, currency=currency,
    ):
        if 0 in [value, requisite.value]:
            continue
        if requisite.value >= value:
            suitable_value = value
        else:
            suitable_value = requisite.value
        suitable_currency_value = round_floor(suitable_value * requisite.rate)
        selected_requisites.append({
            'requisite_id': requisite.id,
            'currency_value': suitable_currency_value,
            'value': suitable_value,
            'rate': requisite.rate,
        })
        value = minus(value, suitable_value)
    currency_value_fix = 0
    value_fix = 0
    for select_requisite in selected_requisites:
        currency_value_fix = plus(currency_value_fix, select_requisite.get('currency_value'))
        value_fix = plus(value_fix, select_requisite.get('value'))
    rate_fix = round_floor(currency_value_fix / value_fix)
    return {
        'selected_requisites': selected_requisites,
        'currency_value': currency_value_fix,
        'value': value_fix,
        'rate_fix': rate_fix,
    }


async def calc_output(
        currency: Currency,
        value: float = None,
        currency_value: float = None,
) -> dict:
    if currency_value:
        return await calc_output_currency2value(currency=currency, currency_value=currency_value)
    elif value:
        return await calc_output_value2currency(currency=currency, value=value)
