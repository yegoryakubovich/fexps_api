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


import asyncio
import logging

from app.db.models import RequestStates, RequestTypes, OrderTypes, Actions
from app.tasks.permanents.requests.states.loading.all import request_type_all
from app.tasks.permanents.requests.states.loading.input import request_type_input
from app.tasks.permanents.requests.states.loading.output import request_type_output
from app.repositories.request import RequestRepository
from app.repositories.requisite import RequisiteRepository
from app.services.base import BaseService
from app.services.order import OrderService
from app.utils.calculations.request.basic import write_other
from app.utils.calculations.request.commissions import get_commission
from app.utils.calculations.request.rates import get_auto_rate
from app.utils.calculations.schemes.loading import RequisiteTypeScheme, AllRequisiteTypeScheme

prefix = '[request_state_loading_check]'


async def request_state_loading_check():
    while True:
        try:
            await run()
        except ValueError as e:
            logging.error(f'{prefix}  Exception \n {e}')


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.LOADING):
        request = await RequestRepository().get_by_id(id_=request.id)
        logging.debug(f'{prefix} request_{request.id} ({request.type}:{request.state}) start check')
        if request.type == RequestTypes.ALL:  # ALL
            result: AllRequisiteTypeScheme = await request_type_all(request=request)
            if not result:
                logging.debug(f'{prefix} request_{request.id} result not found')
                continue
            for input_requisite_scheme in result.input_requisite_type.requisites_scheme_list:
                await OrderService().waited_order_by_scheme(
                    request=request, requisite_scheme=input_requisite_scheme, order_type=OrderTypes.INPUT,
                )
            for output_requisite_scheme in result.output_requisites_type.requisites_scheme_list:
                requisite = await RequisiteRepository().get_by_id(output_requisite_scheme.requisite_id)
                await RequisiteRepository().update(requisite, in_process=False)
            await RequestRepository().update(
                request,
                input_currency_value_raw=result.input_requisite_type.sum_currency_value,
                input_value_raw=result.input_requisite_type.sum_value,
                input_rate_raw=result.input_rate,
                output_currency_value_raw=result.output_requisites_type.sum_currency_value,
                output_value_raw=result.output_requisites_type.sum_value,
                output_rate_raw=result.output_rate,
                commission_value=result.commission_value,
                div_value=0,
            )
        elif request.type == RequestTypes.INPUT:  # INPUT
            result: RequisiteTypeScheme = await request_type_input(request=request)
            if not result:
                logging.debug(f'{prefix} request_{request.id} ({request.type}:{request.state}) result not found')
                continue
            for requisite_scheme in result.requisites_scheme_list:
                await OrderService().waited_order_by_scheme(
                    request=request,
                    requisite_scheme=requisite_scheme,
                    order_type=OrderTypes.INPUT,
                )
            input_rate = get_auto_rate(
                request=request,
                currency_value=result.sum_currency_value,
                value=result.sum_value,
                rate_decimal=request.rate_decimal,
            )
            commission_value = await get_commission(
                request=request,
                wallet_id=request.wallet_id,
                value=result.sum_value,
            )
            await RequestRepository().update(
                request,
                input_currency_value_raw=result.sum_currency_value,
                input_value_raw=result.sum_value,
                input_rate_raw=input_rate,
                commission_value=commission_value,
            )
        elif request.type == RequestTypes.OUTPUT:  # OUTPUT
            result: RequisiteTypeScheme = await request_type_output(request=request)
            if not result:
                logging.debug(f'{prefix} request_{request.id} result not found')
                continue
            for requisite_scheme in result.requisites_scheme_list:
                await OrderService().waited_order_by_scheme(
                    request=request,
                    requisite_scheme=requisite_scheme,
                    order_type=OrderTypes.OUTPUT,
                )
            output_rate = get_auto_rate(
                request=request,
                currency_value=result.sum_currency_value,
                value=result.sum_value,
                rate_decimal=request.rate_decimal,
            )
            await RequestRepository().update(
                request,
                output_currency_value_raw=result.sum_currency_value,
                output_value_raw=result.sum_value,
                output_rate_raw=output_rate,
                commission_value=0,
            )
        await write_other(request=request)
        logging.debug(f'{prefix} request_{request.id} {request.state}->{RequestStates.WAITING}')
        await RequestRepository().update(request, rate_confirmed=True, state=RequestStates.WAITING)
        await BaseService().create_action(
            model=request,
            action=Actions.UPDATE,
            parameters={'state': RequestStates.WAITING},
        )
        await asyncio.sleep(0.25)
    # await asyncio.sleep(0.5)
    await asyncio.sleep(10)
