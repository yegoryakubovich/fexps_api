from typing import List

from app.db.models import Request
from app.utils.calculations.request.commissions import get_commission
from app.utils.calculations.schemes.loading import RequisiteScheme


async def calc_request_value(request: Request, requisites_list: List[RequisiteScheme], type_: str) -> tuple[int, int]:
    raise  # FIXME
    currency_value, value = 0, 0
    for requisite in requisites_list:
        currency_value = round(currency_value + requisite.currency_value)
        value = round(value + requisite.value)
    if type_ == 'input':
        commission_value = await get_commission(wallet_id=request.wallet_id, value=value)
        value = round(value - commission_value)
    return currency_value, value
