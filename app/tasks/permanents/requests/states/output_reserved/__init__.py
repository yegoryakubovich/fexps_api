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

from app.db.models import RequestStates, OrderTypes, OrderStates, RequestFirstLine, Request, RequisiteTypes, \
    RequestTypes, RequisiteStates
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.repositories.requisite import RequisiteRepository
from app.services import TransferSystemService
from app.utils.calculations.request.basic import write_other
from app.utils.calculations.request.difference import get_difference
from app.utils.calculations.request.need_value import output_get_need_currency_value, output_get_need_value
from app.utils.calculations.simples import get_div_by_currency_value, get_div_by_value
from app.utils.service_addons.order import order_banned_value, waited_order

prefix = '[request_state_output_reserved_check]'


async def request_state_output_reserved_check():
    logging.critical('start request_state_output_reserved_check')
    while True:
        try:
            await run()
        except Exception as e:
            logging.error(f'{prefix}  Exception \n {e}')


async def run():
    for request in await RequestRepository().get_list(state=RequestStates.OUTPUT_RESERVATION):
        request = await RequestRepository().get_by_id(id_=request.id)
        _from_value = None
        if request.type == RequestTypes.ALL:
            if request.rate_confirmed:
                logging.critical(f'{_from_value} (1)')
                _from_value = request.output_value_raw
            else:
                logging.critical(f'{_from_value} (2)')
                _from_value = request.input_value
        else:
            logging.critical(f'{_from_value} (3)')
            _from_value = request.output_value_raw
        _need_value = await output_get_need_value(request=request, from_value=_from_value)
        # check wait orders / complete state
        if not _need_value:
            waiting_orders = await OrderRepository().get_list(
                request=request,
                type=OrderTypes.OUTPUT,
                state=OrderStates.WAITING,
            )
            for wait_order in waiting_orders:
                if request.type == RequestTypes.OUTPUT:
                    logging.info(f'{prefix} order_{wait_order.id} banned value = {wait_order.value}')
                    await order_banned_value(wallet=request.wallet, value=wait_order.value)
                logging.info(f'{prefix} order_{wait_order.id} {wait_order.state}->{OrderStates.PAYMENT}')
                await OrderRepository().update(wait_order, state=OrderStates.PAYMENT)
            if not waiting_orders:
                await write_other(request=request)
                logging.info(f'{prefix} request_{request.id} {request.state}->{RequestStates.OUTPUT}')
                await RequestRepository().update(request, state=RequestStates.OUTPUT)  # Started next state
            continue
        # create missing orders
        if request.type == RequestTypes.ALL:
            if request.rate_confirmed:
                _from_value = request.output_value_raw
            else:
                _from_value = request.input_value
        else:
            _from_value = request.output_value_raw
        need_value = await output_get_need_value(request=request, from_value=_from_value)
        logging.info(f'create missing orders request_{request.id} need_value = {need_value}')
        await get_new_requisite_by_value(request=request, need_value=need_value)
        await write_other(request=request)
        difference_value = get_difference(request=request)
        if request.difference_confirmed != difference_value:
            logging.info(f'{prefix} request_{request.id} '
                         f'difference_value {difference_value} '
                         f'difference_confirmed= {request.difference_confirmed} ')
            await TransferSystemService().payment_difference(
                request=request,
                value=difference_value - request.difference_confirmed,
                from_banned_value=True,
            )
            await RequestRepository().update(request, difference_confirmed=difference_value)
        await asyncio.sleep(0.25)
    await asyncio.sleep(0.5)


async def get_new_requisite_by_currency_value(
        request: Request,
        need_currency_value: int,
) -> None:
    currency = request.output_method.currency
    for requisite in await RequisiteRepository().get_list_output_by_rate(
            type=RequisiteTypes.INPUT,
            state=RequisiteStates.ENABLE,
            currency=currency,
            in_process=False,
    ):
        await RequisiteRepository().update(requisite, in_process=True)
        rate_decimal, requisite_rate_decimal = request.rate_decimal, requisite.currency.rate_decimal
        requisite_rate = requisite.rate
        if rate_decimal != requisite_rate_decimal:
            requisite_rate = round(requisite.rate / 10 ** requisite_rate_decimal * 10 ** rate_decimal)
        _need_currency_value = need_currency_value
        # Zero check
        if 0 in [_need_currency_value, requisite.currency_value]:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        # Min/Max check
        if requisite.currency_value_min and _need_currency_value < requisite.currency_value_min:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        if requisite.currency_value_max and _need_currency_value > requisite.currency_value_max:
            _need_currency_value = requisite.currency_value_max
        # Div check
        if _need_currency_value < currency.div:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        # Check max possible value
        if requisite.currency_value >= _need_currency_value:
            suitable_currency_value = _need_currency_value
        else:
            suitable_currency_value = requisite.currency_value
        # Check TRUE
        suitable_currency_value, suitable_value = get_div_by_currency_value(  # Rounded value
            currency_value=suitable_currency_value,
            div=currency.div,
            rate=requisite_rate,
            rate_decimal=rate_decimal,
            order_type=OrderTypes.OUTPUT,
        )
        if not suitable_currency_value or not suitable_value:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        await waited_order(
            request=request,
            requisite=requisite,
            currency_value=suitable_currency_value,
            value=suitable_value,
            rate=requisite.rate,
            order_type=OrderTypes.OUTPUT,
        )
        need_currency_value = round(need_currency_value - suitable_currency_value)


async def get_new_requisite_by_value(
        request: Request,
        need_value: int,
) -> None:
    currency = request.output_method.currency
    for requisite in await RequisiteRepository().get_list_output_by_rate(
            type=RequisiteTypes.INPUT,
            state=RequisiteStates.ENABLE,
            currency=currency,
            in_process=False,
    ):
        await RequisiteRepository().update(requisite, in_process=True)
        rate_decimal, requisite_rate_decimal = request.rate_decimal, requisite.currency.rate_decimal
        requisite_rate = requisite.rate
        if rate_decimal != requisite_rate_decimal:
            requisite_rate = round(requisite.rate / 10 ** requisite_rate_decimal * 10 ** rate_decimal)
        _need_value = need_value
        # Zero check
        if 0 in [_need_value, requisite.value]:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        # Min/Max check
        if requisite.value_min and _need_value < requisite.value_min:  # Меньше минимума
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        if requisite.value_max and _need_value > requisite.value_max:  # Больше максимума
            _need_value = requisite.value_max
        # Div check
        if round(_need_value * requisite_rate / 10 ** rate_decimal) < currency.div:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        # Check max possible value
        if requisite.value >= _need_value:
            suitable_value = _need_value
        else:
            suitable_value = requisite.value
        # Check TRUE
        suitable_currency_value, suitable_value = get_div_by_value(
            value=suitable_value,
            div=currency.div,
            rate=requisite_rate,
            rate_decimal=rate_decimal,
            type_=OrderTypes.OUTPUT,
        )
        if not suitable_currency_value or not suitable_value:
            await RequisiteRepository().update(requisite, in_process=False)
            continue
        await waited_order(
            request=request,
            requisite=requisite,
            currency_value=suitable_currency_value,
            value=suitable_value,
            rate=requisite.rate,
            order_type=OrderTypes.OUTPUT,
        )
        need_value = round(need_value - suitable_value)
