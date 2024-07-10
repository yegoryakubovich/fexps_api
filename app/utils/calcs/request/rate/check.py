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


from app.db.models import Request, RequestTypes, RequestStates
from app.repositories import RequestRepository
from app.utils.calcs.request.rate.all import calcs_request_rate_all
from app.utils.calcs.request.rate.input import calcs_request_rate_input
from app.utils.calcs.request.rate.output import calcs_request_rate_output


async def calcs_request_check_rate(request: Request):
    # check rate_fixed
    if request.rate_fixed:
        return
    # start check rate
    if request.state == RequestStates.INPUT_RESERVATION and request.type == RequestTypes.ALL:
        calculate = await calcs_request_rate_all(
            input_method=request.input_method,
            output_method=request.output_method,
            commission_pack=request.wallet.commission_pack,
            input_currency_value=request.input_currency_value,
        )
        if not calculate:
            return
        if request.output_currency_value < calculate.output_currency_value:
            return
        await RequestRepository().update(
            request,
            commission=calculate.commission,
            rate=calculate.rate,
            input_currency_value=calculate.input_currency_value,
            input_rate=calculate.input_rate,
            input_value=calculate.input_value,
            output_currency_value=calculate.output_currency_value,
            output_rate=calculate.output_rate,
            output_value=calculate.output_value,
        )
    elif request.state == RequestStates.INPUT_RESERVATION and request.type == RequestTypes.INPUT:
        calculate = await calcs_request_rate_input(
            input_method=request.input_method,
            commission_pack=request.wallet.commission_pack,
            input_currency_value=request.input_currency_value,
        )
        if not calculate:
            return
        if request.input_value < calculate.input_value:
            return
        await RequestRepository().update(
            request,
            commission=calculate.commission,
            rate=calculate.rate,
            input_currency_value=calculate.input_currency_value,
            input_rate=calculate.input_rate,
            input_value=calculate.input_value,
        )
    elif request.state == RequestStates.OUTPUT_RESERVATION and request.type in [RequestTypes.OUTPUT, RequestTypes.ALL]:
        calculate = await calcs_request_rate_output(
            output_method=request.output_method,
            output_value=request.output_value,
        )
        if not calculate:
            return
        if request.output_currency_value < calculate.output_currency_value:
            return
        await RequestRepository().update(
            request,
            rate=calculate.rate,
            output_currency_value=calculate.output_currency_value,
            output_rate=calculate.output_rate,
            output_value=calculate.output_value,
        )
