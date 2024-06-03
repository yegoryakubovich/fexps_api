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
import math

from app.db.models import RequestStates, RequestTypes, Actions, RequestFirstLine, NotificationTypes
from app.repositories.request import RequestRepository
from app.services.base import BaseService
from app.tasks.permanents.requests.logger import RequestLogger
from app.utils.bot.notification import BotNotification
from app.utils.calculations.request.basic import write_other
from app.utils.calculations.request.rates import get_auto_rate
from .all import request_type_all
from .input import request_type_input
from .output import request_type_output

custom_logger = RequestLogger(prefix='request_state_loading_check')


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.LOADING):
        request = await RequestRepository().get_by_id(id_=request.id)
        custom_logger.info(text='start check', request=request)
        if request.type == RequestTypes.ALL:  # ALL
            result_all_type = await request_type_all(request=request)
            if not result_all_type:
                custom_logger.info(text='all result not found', request=request)
                continue
            rate = get_auto_rate(
                request=request,
                currency_value=result_all_type.input_type.currency_value,
                value=result_all_type.output_type.currency_value,
            )
            await RequestRepository().update(
                request,
                input_currency_value_raw=result_all_type.input_type.currency_value,
                input_value_raw=result_all_type.input_type.value,
                input_rate_raw=result_all_type.input_rate,
                output_currency_value_raw=result_all_type.output_type.currency_value,
                output_value_raw=result_all_type.output_type.value,
                output_rate_raw=result_all_type.output_rate,
                commission_value=result_all_type.commission_value,
                rate=rate,
                div_value=0,
            )
        elif request.type == RequestTypes.INPUT:  # INPUT
            currency_value, value = None, None
            if request.first_line == RequestFirstLine.INPUT_CURRENCY_VALUE:
                currency_value = request.first_line_value
            elif request.first_line == RequestFirstLine.INPUT_VALUE:
                value = request.first_line_value
            result_type = await request_type_input(request=request, currency_value=currency_value, value=value)
            if not result_type:
                custom_logger.warning(text='input result not found', request=request)
                continue
            input_rate = get_auto_rate(
                request=request,
                currency_value=result_type.currency_value,
                value=result_type.value,
            )
            await RequestRepository().update(
                request,
                input_currency_value_raw=result_type.currency_value,
                input_value_raw=result_type.value,
                input_rate_raw=input_rate,
                commission_value=result_type.commission_value,
                rate=input_rate,
            )
        elif request.type == RequestTypes.OUTPUT:  # OUTPUT
            currency_value, value = None, None
            if request.first_line == RequestFirstLine.OUTPUT_CURRENCY_VALUE:
                currency_value = request.first_line_value
            elif request.first_line == RequestFirstLine.OUTPUT_VALUE:
                value = request.first_line_value
            result_type = await request_type_output(request=request, currency_value=currency_value, value=value)
            if not result_type:
                custom_logger.info(text='output result not found', request=request)
                continue
            output_rate = get_auto_rate(
                request=request,
                currency_value=result_type.currency_value,
                value=result_type.value,
            )
            await RequestRepository().update(
                request,
                output_currency_value_raw=result_type.currency_value,
                output_value_raw=result_type.value,
                output_rate_raw=output_rate,
                commission_value=result_type.commission_value,
                rate=output_rate,
            )
        await write_other(request=request)
        custom_logger.info(text=f'{request.state}->{RequestStates.WAITING}', request=request)
        await RequestRepository().update(request, rate_confirmed=True, state=RequestStates.WAITING)
        await BotNotification().send_notification_by_wallet(
            wallet=request.wallet,
            notification_type=NotificationTypes.REQUEST,
            text_key=f'notification_request_update_state_{RequestStates.WAITING}',
            request_id=request.id,
        )
        await BaseService().create_action(
            model=request,
            action=Actions.UPDATE,
            parameters={'state': RequestStates.WAITING},
        )
        await asyncio.sleep(1)
    await asyncio.sleep(5)


async def request_state_loading_check():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
