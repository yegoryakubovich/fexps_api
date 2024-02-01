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


from app.db.models import Session, Request, OrderTypes, Actions, RequestStates, RequestTypes
from app.repositories.method import MethodRepository
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.repositories.requisite_data import RequisiteDataRepository
from app.repositories.wallet import WalletRepository
from app.services.base import BaseService
from app.services.order import OrderService
from app.utils.calculations.orders import calc_all
from app.utils.calculations.orders.input import calc_input
from app.utils.calculations.orders.output import calc_output
from app.utils.calculations.orders.utils.hard import get_need_values_input, get_need_values_output
from app.utils.decorators import session_required


class RequestService(BaseService):
    model = Request

    @session_required(permissions=['requests'])
    async def create(
            self,
            session: Session,
            wallet_id: int,
            type_: str,
            input_method_id: int,
            input_currency_value: int,
            input_value: int,
            output_currency_value: int,
            output_value: int,
            output_requisite_data_id: int,
    ) -> dict:
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        input_method = None
        if input_method_id:
            input_method = await MethodRepository().get_by_id(id_=input_method_id)
        output_method = None
        output_requisite_data = None
        if output_requisite_data_id:
            output_requisite_data = await RequisiteDataRepository().get_by_id(id_=output_requisite_data_id)
            output_method = output_requisite_data.method
        request = await RequestRepository().create(
            wallet=wallet,
            state=RequestStates.WAITING,
            type=type_,
            input_currency_value=input_currency_value,
            input_value=input_value,
            input_method=input_method,
            output_currency_value=output_currency_value,
            output_value=output_value,
            output_method=output_method,
            output_requisite_data=output_requisite_data,
        )
        await self.create_action(
            model=request,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'id': request.id,
                'wallet_id': wallet_id,
                'input_currency_value': input_currency_value,
                'input_value': input_value,
                'input_method': input_method,
                'output_currency_value': output_currency_value,
                'output_value': output_value,
                'output_method': output_method,
                'output_requisite_data': output_requisite_data,
            },
        )
        await self.create_relation(request=request)

        return {'request_id': request.id}

    @staticmethod
    async def create_relation_input(request: Request) -> None:
        currency = request.input_method.currency
        print(RequestTypes.INPUT)
        need_input_value, need_value = await get_need_values_input(
            request=request, order_type=OrderTypes.INPUT,
        )
        input_calc = await calc_input(
            request=request, currency=currency, currency_value=need_input_value, value=need_value,
        )
        for calc_requisite in input_calc.calc_requisites:
            await OrderService().reserve_order(
                request=request, calc_requisite=calc_requisite, order_type=OrderTypes.INPUT,
            )
        await OrderRepository().update(
            request,
            input_currency_value=input_calc.currency_value,
            input_value=input_calc.value,
            input_rate=input_calc.rate,
            commission_value=input_calc.commission_value,
            div_value=input_calc.div_value,
            rate=input_calc.rate,
        )

    @staticmethod
    async def create_relation_output(request: Request) -> None:
        currency = request.output_method.currency
        print(RequestTypes.OUTPUT)
        need_output_value, need_value = await get_need_values_output(
            request=request, order_type=OrderTypes.OUTPUT,
        )
        output_calc = await calc_output(
            request=request, currency=currency, currency_value=need_output_value, value=need_value
        )
        for calc_requisite in output_calc.calc_requisites:
            await OrderService().waited_order(
                request=request, calc_requisite=calc_requisite, order_type=OrderTypes.OUTPUT,
            )
        await OrderRepository().update(
            request,
            commission_value=output_calc.commission_value,
            div_value=output_calc.div_value,
            rate=output_calc.rate,
            output_currency_value=output_calc.currency_value,
            output_value=output_calc.value,
            output_rate=output_calc.rate,
        )

    @staticmethod
    async def create_relation_all(request: Request) -> None:
        print(RequestTypes.ALL)
        input_currency = request.input_method.currency
        output_currency = request.output_method.currency
        calc_requisites = await calc_all(
            request=request,
            currency_input=input_currency, input_currency_value=request.input_currency_value,
            currency_output=output_currency, output_currency_value=request.output_currency_value,
        )
        for calc_requisite_input in calc_requisites.input_calc.calc_requisites:
            await OrderService().reserve_order(
                request=request, calc_requisite=calc_requisite_input, order_type=OrderTypes.INPUT,
            )
        for calc_requisite_output in calc_requisites.output_calc.calc_requisites:
            await OrderService().waited_order(
                request=request, calc_requisite=calc_requisite_output, order_type=OrderTypes.OUTPUT,
            )
        await OrderRepository().update(
            request,
            input_currency_value=calc_requisites.input_currency_value,
            input_value=calc_requisites.input_value,
            input_rate=calc_requisites.input_calc.rate,
            commission_value=calc_requisites.commission_value,
            div_value=calc_requisites.div_value,
            rate=calc_requisites.rate,
            output_currency_value=calc_requisites.output_currency_value,
            output_value=calc_requisites.output_value,
            output_rate=calc_requisites.output_calc.rate,
        )

    async def create_relation(self, request: Request) -> None:
        if request.type == RequestTypes.INPUT:
            await self.create_relation_input(request=request)
        elif request.type == RequestTypes.OUTPUT:
            await self.create_relation_output(request=request)
        elif request.type == RequestTypes.ALL:
            await self.create_relation_all(request=request)

    @session_required(permissions=['requests'])
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        request = await RequestRepository().get_by_id(id_=id_)
        for order in await OrderRepository().get_list(request=request):
            await OrderService().delete(session=session, id_=order.id)
        await RequestRepository().delete(request)
        await self.create_action(
            model=request,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )

        return {}

    @staticmethod
    async def get_need_value(
            request: Request,
            type_: OrderTypes,
            currency_value: int = None,
            value: int = None,
    ) -> int:
        if not value and not currency_value:
            return 0
        result = value or currency_value
        for order in await OrderRepository().get_list(request=request, type=type_):
            if value:  # value
                result -= order.value
            else:  # currency value
                result -= order.currency_value
        return result
