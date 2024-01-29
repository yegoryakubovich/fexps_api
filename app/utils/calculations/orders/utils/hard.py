#
# (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import math
from typing import List
from typing import Optional

from app.db.models import CommissionPackValue
from app.db.models import Request, OrderStates
from app.repositories.commission_pack_value import CommissionPackValueRepository
from app.repositories.order import OrderRepository
from app.repositories.wallet import WalletRepository
from app.services.commission_pack_value import IntervalNotFoundError
from app.utils.schemes.calculations.orders import CalcRequisiteScheme


async def get_need_values_input(request: Request, order_type: str) -> tuple[Optional[int], Optional[int]]:
    result_currency_value, result_value = request.input_currency_value, request.input_value
    for order in await OrderRepository().get_list(request=request, type=order_type):
        if order.state == OrderStates.CANCELED:
            continue
        if request.input_currency_value:
            result_currency_value = round(result_currency_value - order.currency_value)
        if request.input_value:
            result_value = round(result_value - order.value)
    print(f'result_currency_value: {request.input_currency_value} -> {result_currency_value}')
    print(f'result_value: {request.input_value} -> {result_value}')
    return result_currency_value, result_value


async def get_need_values_output(request: Request, order_type: str) -> tuple[Optional[int], Optional[int]]:
    result_currency_value, result_value = request.output_currency_value, request.output_value
    for order in await OrderRepository().get_list(request=request, type=order_type):
        if order.state == OrderStates.CANCELED:
            continue
        if request.output_currency_value:
            result_currency_value = round(result_currency_value - order.currency_value)
        if request.output_value:
            result_value = round(result_value - order.value)
    print(f'result_currency_value: {request.output_currency_value} -> {result_currency_value}')
    print(f'result_value: {request.output_value} -> {result_value}')
    return result_currency_value, result_value


def get_results_by_calc_requisites(
        calc_requisites: List[CalcRequisiteScheme],
        type_: str,
) -> tuple[int, int, int]:
    currency_value_result, value_result = 0, 0
    for calc_requisite in calc_requisites:
        currency_value_result = round(currency_value_result + calc_requisite.currency_value)
        value_result = round(value_result + calc_requisite.value)
    print(f'currency_value_result={currency_value_result}')
    print(f'value_result={value_result}')
    if type_ == 'input':
        rate_result = math.ceil(currency_value_result / value_result * 100)
    else:
        rate_result = math.floor(currency_value_result / value_result * 100)
    return currency_value_result, value_result, rate_result


def get_commission_value(value: int, commission_pack_value: CommissionPackValue) -> int:
    result = 0
    if commission_pack_value.percent:
        result += round(value * commission_pack_value.percent / 10000)
    if commission_pack_value.value:
        result += commission_pack_value.value
    return result


async def get_commission(wallet_id: int, value: int) -> int:
    wallet = await WalletRepository().get_by_id(id_=wallet_id)
    commission_pack_value = await CommissionPackValueRepository().get_by_value(
        commission_pack=wallet.commission_pack,
        value=value,
    )
    if not commission_pack_value:
        raise IntervalNotFoundError(f'By value == "{value}" not found suitable interval')
    return get_commission_value(value=value, commission_pack_value=commission_pack_value)
