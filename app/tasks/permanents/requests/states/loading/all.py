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

from app.db.models import Request, RequestFirstLine
from app.tasks.permanents.requests.states.loading.input import request_type_input_currency_value, request_type_input_value
from app.tasks.permanents.requests.states.loading.output import request_type_output_value, request_type_output_currency_value
from app.repositories.requisite import RequisiteRepository
from app.utils.calculations.request.commissions import get_commission
from app.utils.calculations.request.need_value import input_get_need_currency_value, output_get_need_value, \
    output_get_need_currency_value, input_get_need_value
from app.utils.calculations.request.rates import get_auto_rate
from app.utils.calculations.schemes.loading import AllRequisiteTypeScheme

prefix = '[request_type_all]'


async def request_type_all(
        request: Request,
) -> Optional[AllRequisiteTypeScheme]:
    logging.info(f'{prefix} start')
    if request.first_line == RequestFirstLine.INPUT_CURRENCY_VALUE:
        need_input_currency_value = await input_get_need_currency_value(request=request)
        logging.info(f'req_{request.id} INPUT_CV, need_input_currency_value={need_input_currency_value}')
        input_result = await request_type_input_currency_value(
            request=request,
            currency=request.input_method.currency,
            need_currency_value=need_input_currency_value,
        )
        if not input_result:
            return
        input_rate = get_auto_rate(
            request=request,
            currency_value=input_result.sum_currency_value,
            value=input_result.sum_value,
            rate_decimal=request.rate_decimal,
        )
        commission_value = await get_commission(
            request=request,
            wallet_id=request.wallet_id,
            value=input_result.sum_value,
        )
        _output_from_value = input_result.sum_value - commission_value
        need_output_value = await output_get_need_value(request=request, from_value=_output_from_value)
        logging.info(f'req_{request.id} OUTPUT_V, need_output_value={need_output_value}')
        output_result = await request_type_output_value(
            request=request,
            currency=request.output_method.currency,
            need_value=need_output_value,
        )
        if not output_result:
            for input_requisite_scheme in input_result.requisites_scheme_list:
                requisite = await RequisiteRepository().get_by_id(input_requisite_scheme.requisite_id)
                await RequisiteRepository().update(requisite, in_process=False)
            return
        output_rate = get_auto_rate(
            request=request,
            currency_value=output_result.sum_currency_value,
            value=output_result.sum_value,
            rate_decimal=request.rate_decimal,
        )
        return AllRequisiteTypeScheme(
            input_requisite_type=input_result,
            output_requisites_type=output_result,
            input_rate=input_rate,
            output_rate=output_rate,
            commission_value=commission_value
        )
    elif request.first_line == RequestFirstLine.OUTPUT_CURRENCY_VALUE:
        need_output_currency_value = await output_get_need_currency_value(request=request)
        logging.info(f'req_{request.id} OUTPUT_CV, need_output_currency_value={need_output_currency_value}')
        output_result = await request_type_output_currency_value(
            request=request,
            currency=request.output_method.currency,
            need_currency_value=need_output_currency_value,
        )
        if not output_result:
            return
        output_rate = get_auto_rate(
            request=request,
            currency_value=output_result.sum_currency_value,
            value=output_result.sum_value,
            rate_decimal=request.rate_decimal,
        )
        commission_value = await get_commission(
            request=request,
            wallet_id=request.wallet_id,
            value=output_result.sum_value,
        )
        _input_from_value = output_result.sum_value + commission_value
        need_input_value = await input_get_need_value(request=request, from_value=_input_from_value)
        logging.info(f'req_{request.id} INPUT_V, need_input_value={need_input_value}')
        input_result = await request_type_input_value(
            request=request,
            currency=request.input_method.currency,
            need_value=need_input_value,
        )
        if not input_result:
            for output_requisite_scheme in output_result.requisites_scheme_list:
                requisite = await RequisiteRepository().get_by_id(output_requisite_scheme.requisite_id)
                await RequisiteRepository().update(requisite, in_process=False)
            return
        input_rate = get_auto_rate(
            request=request,
            currency_value=input_result.sum_currency_value,
            value=input_result.sum_value,
            rate_decimal=request.rate_decimal,
        )
        return AllRequisiteTypeScheme(
            input_requisite_type=input_result,
            output_requisites_type=output_result,
            input_rate=input_rate,
            output_rate=output_rate,
            commission_value=commission_value
        )
