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
from typing import Optional

from app.db.models import Method, RequisiteStates, RequisiteTypes, Request, RequestRequisiteTypes
from app.repositories import RequisiteRepository, RequestRequisiteRepository
from app.utils.calculations.requisites.check_empty import calculate_requisite_check_empty
from app.utils.calculations.requisites.process_change import calculate_requisite_process_change, \
    calculate_requisite_process_change_list
from app.utils.calculations.requisites.suitable_value import calculate_requisite_suitable_from_currency_value
from app.utils.schemes.calculations.rate import RequisiteDataScheme, RequisiteItemScheme
from app.utils.value import value_to_int


async def calculate_requisite_output_by_currency_value(
        method: Method,
        currency_value: int,
        process: bool = False,
request: Request = None,
) -> Optional[RequisiteDataScheme]:
    need_currency_value = currency_value
    requisite_items = []
    result_currency_value, result_value = 0, 0
    requisite_params = {'type': RequisiteTypes.INPUT, 'input_method': method, 'state': RequisiteStates.ENABLE}
    if process:
        requisite_params['in_process'] = False
    for requisite in await RequisiteRepository().get_list_input_by_rate(**requisite_params):
        await calculate_requisite_process_change(requisite=requisite, in_process=True, process=process)
        if request:
            if request.wallet.id == requisite.wallet.id:
                await calculate_requisite_process_change(requisite=requisite, in_process=False, process=process)
                continue
            if await RequestRequisiteRepository().get(
                    request=request,
                    requisite=requisite,
                    type=RequestRequisiteTypes.BLACKLIST,
            ):
                await calculate_requisite_process_change(requisite=requisite, in_process=False, process=process)
                continue
        # Check need_value
        if not need_currency_value:
            await calculate_requisite_process_change(requisite=requisite, in_process=False, process=process)
            break
        # Check balance
        if await calculate_requisite_check_empty(requisite=requisite):
            await calculate_requisite_process_change(requisite=requisite, in_process=False, process=process)
            continue
        # Find suitable value
        suitable_result = await calculate_requisite_suitable_from_currency_value(
            requisite=requisite,
            need_currency_value=need_currency_value,
        )
        if not suitable_result:
            await calculate_requisite_process_change(requisite=requisite, in_process=False, process=process)
            continue
        suitable_currency_value, suitable_value = suitable_result
        requisite_items.append(RequisiteItemScheme(
            requisite_id=requisite.id,
            currency_value=suitable_currency_value,
            value=suitable_value,
        ))
        need_currency_value -= suitable_currency_value
        result_currency_value += suitable_currency_value
        result_value += suitable_value
    if not result_currency_value or not result_value:
        await calculate_requisite_process_change_list(
            requisites=[requisite_item.requisite_id for requisite_item in requisite_items],
            in_process=False,
            process=process,
        )
        return
    if need_currency_value > method.currency.div:
        await calculate_requisite_process_change_list(
            requisites=[requisite_item.requisite_id for requisite_item in requisite_items],
            in_process=False,
            process=process,
        )
        return
    rate_float = result_currency_value / result_value
    rate = value_to_int(value=rate_float, decimal=method.currency.rate_decimal, round_method=math.floor)
    return RequisiteDataScheme(
        requisite_items=requisite_items,
        currency_value=result_currency_value,
        rate=rate,
        value=result_value,
    )
