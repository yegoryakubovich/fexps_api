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


from typing import Optional

from app.db.models import Request, RequestFirstLine
from app.tasks.permanents.requests.logger import RequestLogger
from app.tasks.permanents.requests.states.loading.input import request_type_input
from app.tasks.permanents.requests.states.loading.output import request_type_output
from app.utils.calculations.request.commissions import get_commission
from app.utils.calculations.request.rates import get_auto_rate
from app.utils.calculations.schemes.loading import AllTypeScheme

custom_logger = RequestLogger(prefix='request_state_loading_all_check')


async def request_type_all(
        request: Request,
) -> Optional[AllTypeScheme]:
    custom_logger.info(text='start check', request=request)
    currency_value = request.first_line_value
    input_result_type, output_result_type = None, None
    input_rate, output_rate = None, None
    if request.first_line == RequestFirstLine.INPUT_CURRENCY_VALUE:
        custom_logger.info(text=f'input_currency_value={currency_value}', request=request)
        input_result_type = await request_type_input(request=request, currency_value=currency_value)
        if not input_result_type:
            return
        input_rate = get_auto_rate(
            request=request,
            currency_value=input_result_type.currency_value,
            value=input_result_type.value,
        )
        output_from_value = input_result_type.value - input_result_type.commission_value
        custom_logger.info(text=f'output_from_value={output_from_value}', request=request)
        output_result_type = await request_type_output(request=request, value=output_from_value)
        if not output_result_type:
            return
        output_rate = get_auto_rate(
            request=request,
            currency_value=output_result_type.currency_value,
            value=output_result_type.value,
        )
    elif request.first_line == RequestFirstLine.OUTPUT_CURRENCY_VALUE:
        output_result_type = await request_type_output(request=request, currency_value=currency_value)
        if not output_result_type:
            return
        output_rate = get_auto_rate(
            request=request,
            currency_value=output_result_type.currency_value,
            value=output_result_type.value,
        )
        commission_value = await get_commission(
            request=request,
            wallet_id=request.wallet_id,
            value=output_result_type.value,
        )
        input_from_value = output_result_type.value + commission_value
        input_result_type = await request_type_input(request=request, value=input_from_value)
        if not input_result_type:
            return
        input_rate = get_auto_rate(
            request=request,
            currency_value=input_result_type.currency_value,
            value=input_result_type.value,
        )
    commission_value = input_result_type.commission_value + output_result_type.commission_value
    return AllTypeScheme(
        input_type=input_result_type,
        output_type=output_result_type,
        input_rate=input_rate,
        output_rate=output_rate,
        commission_value=commission_value,
    )
