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
import logging
from typing import Optional

from app.db.models import Method, RequisiteStates, RequisiteTypes, Request, RequestRequisiteTypes
from app.repositories import RequisiteRepository, RequestRequisiteRepository
from app.utils.calcs.requisites.check_empty import calcs_requisite_check_empty
from app.utils.calcs.requisites.process_change import calcs_requisite_process_change, \
    calcs_requisite_process_change_list
from app.utils.calcs.requisites.suitable_value import calcs_requisite_suitable_from_currency_value
from app.utils.schemes.calcs.rate import RequisiteDataScheme, RequisiteItemScheme


async def calcs_requisite_output_by_currency_value(
        method: Method,
        currency_value: int,
        process: bool = False,
        request: Request = None,
) -> Optional[RequisiteDataScheme]:
    logging.critical(2)
    need_currency_value = currency_value
    requisite_items = []
    result_currency_value, result_value = 0, 0
    requisite_params = {'type': RequisiteTypes.INPUT, 'input_method': method, 'state': RequisiteStates.ENABLE}
    if process:
        logging.critical(2)
        requisite_params['in_process'] = False
    for requisite in await RequisiteRepository().get_list_input_by_rate(**requisite_params):
        logging.critical(2)
        await calcs_requisite_process_change(requisite=requisite, in_process=True, process=process)
        if request and await RequestRequisiteRepository().get(
                request=request,
                requisite=requisite,
                type=RequestRequisiteTypes.BLACKLIST,
        ):
            logging.critical(2)
            await calcs_requisite_process_change(requisite=requisite, in_process=False, process=process)
            continue
        # Check need_value
        if not need_currency_value:
            logging.critical(2)
            await calcs_requisite_process_change(requisite=requisite, in_process=False, process=process)
            break
        # Check balance
        if await calcs_requisite_check_empty(requisite=requisite):
            logging.critical(2)
            await calcs_requisite_process_change(requisite=requisite, in_process=False, process=process)
            continue
        # Find suitable value
        logging.critical(2)
        suitable_result = await calcs_requisite_suitable_from_currency_value(
            requisite=requisite,
            need_currency_value=need_currency_value,
        )
        logging.critical(2)
        if not suitable_result:
            await calcs_requisite_process_change(requisite=requisite, in_process=False, process=process)
            continue
        logging.critical(2)
        suitable_currency_value, suitable_value = suitable_result
        # Finish find requisite
        logging.critical(2)
        requisite_items += [
            RequisiteItemScheme(
                requisite_id=requisite.id,
                currency_value=suitable_currency_value,
                value=suitable_value,
            ),
        ]
        logging.critical(2)
        need_currency_value -= suitable_currency_value
        result_currency_value += suitable_currency_value
    # check exist result_currency_value
    logging.critical(2)
    logging.critical('\n'.join([
        f'need_currency_value={need_currency_value}',
        f'result_currency_value={result_currency_value}',
        f'requisite_items={requisite_items} ({len(requisite_items)})',
    ]))
    if not result_currency_value:
        logging.critical(2)
        await calcs_requisite_process_change_list(
            requisites=[requisite_item.requisite_id for requisite_item in requisite_items],
            in_process=False,
            process=process,
        )
        return
    logging.critical(2)
    # check fill need currency value complete
    if need_currency_value > method.currency.div:
        logging.critical(2)
        await calcs_requisite_process_change_list(
            requisites=[requisite_item.requisite_id for requisite_item in requisite_items],
            in_process=False,
            process=process,
        )
        return

    logging.critical(2)
    return RequisiteDataScheme(requisite_items=requisite_items, currency_value=result_currency_value)
