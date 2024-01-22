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


from app.db.models import Session, Request, OrderTypes, Actions, RequestTypes, OrderStates
from app.repositories.method import MethodRepository
from app.repositories.order import OrderRepository
from app.repositories.request import RequestRepository
from app.repositories.requisite_data import RequisiteDataRepository
from app.repositories.wallet import WalletRepository
from app.services.base import BaseService
from app.services.order import OrderService
from app.utils.decorators import session_required


class RequestService(BaseService):
    model = Request

    @session_required()
    async def create(
            self,
            session: Session,
            wallet_id: int,
            type_: str,
            input_method_id: int,
            input_value: float,
            value: float,
            output_requisite_data_id: int,
            output_value: float,
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
            type=type_,
            input_method=input_method,
            input_value=input_value,
            value=value,
            output_method=output_method,
            output_requisite_data=output_requisite_data,
            output_value=output_value,
        )
        await self.create_action(
            model=request,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'id': request.id,
                'wallet_id': wallet_id,
                'input_method_id': input_method_id,
                'input_value': input_value,
                'value': value,
                'output_requisite_data_id': output_requisite_data_id,
                'output_value': output_value,
            },
        )

        return {'request_id': request.id}

    @session_required()
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

    @staticmethod
    async def check_all_orders(request: Request) -> None:
        if request.type in [RequestTypes.INPUT, RequestTypes.ALL]:
            input_orders = await OrderRepository().get_list(request=request, type=OrderTypes.INPUT)
            input_compete_count, input_wait_count, input_count = 0, 0, 0
            for input_order in input_orders:
                if input_order.type in [OrderStates.CANCELED]:
                    continue
                elif input_order.type in [OrderStates.RESERVE, OrderStates.PAYMENT, OrderStates.CONFIRMATION]:
                    input_wait_count += 1
                elif input_order.type in [OrderStates.COMPLETED]:
                    input_compete_count += 1
                input_count += 1

        if request.type in [RequestTypes.OUTPUT, RequestTypes.ALL]:
            output_orders = await OrderRepository().get_list(request=request, type=OrderTypes.OUTPUT)
            output_compete_count, output_wait_count, output_count = 0, 0, 0
            for output_order in output_orders:
                if output_order.type in [OrderStates.CANCELED]:
                    continue
                elif output_order.type in [OrderStates.RESERVE, OrderStates.PAYMENT, OrderStates.CONFIRMATION]:
                    output_wait_count += 1
                elif output_order.type in [OrderStates.COMPLETED]:
                    output_compete_count += 1
                output_count += 1

