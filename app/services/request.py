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


from app.db.models import Session, Request, Actions, RequestStates, RequestTypes, RequestFirstLine
from app.repositories.method import MethodRepository
from app.repositories.request import RequestRepository
from app.repositories.requisite_data import RequisiteDataRepository
from app.repositories.wallet import WalletRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions.request import RequestStateWrong, RequestStateNotPermission
from app.utils.exceptions.wallet import NotEnoughFundsOnBalance
from app.utils.service_addons.wallet import wallet_check_permission


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
        first_line, first_line_value = None, None
        input_method, output_requisite_data, output_method = None, None, None
        if input_currency_value:
            first_line = RequestFirstLine.INPUT_CURRENCY_VALUE
            first_line_value = input_currency_value
        elif input_value:
            first_line = RequestFirstLine.INPUT_VALUE
            first_line_value = input_value
        elif output_currency_value:
            first_line = RequestFirstLine.OUTPUT_CURRENCY_VALUE
            first_line_value = output_currency_value
        elif output_value:
            first_line = RequestFirstLine.OUTPUT_VALUE
            first_line_value = output_value
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        rate_decimal = []
        if input_method_id:
            input_method = await MethodRepository().get_by_id(id_=input_method_id)
            rate_decimal.append(input_method.currency.rate_decimal)
        if output_requisite_data_id:
            output_requisite_data = await RequisiteDataRepository().get_by_id(id_=output_requisite_data_id)
            output_method = output_requisite_data.method
            rate_decimal.append(output_method.currency.rate_decimal)
        if type_ == RequestTypes.OUTPUT and output_value:
            balance = wallet.value - wallet.value_can_minus
            if output_value > balance:
                raise NotEnoughFundsOnBalance()
        request = await RequestRepository().create(
            wallet=wallet,
            state=RequestStates.LOADING,
            type=type_,
            rate_decimal=max(rate_decimal),
            first_line=first_line,
            first_line_value=first_line_value,
            input_method=input_method,
            output_requisite_data=output_requisite_data,
            output_method=output_method,
        )
        await self.create_action(
            model=request,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'id': request.id,
                'wallet_id': wallet_id,
                'first_line': first_line,
                'first_line_value': input_currency_value,
                'input_method_id': input_method.id,
                'output_requisite_data_id': output_requisite_data.id,
                'output_method_id': output_method.id,
            },
        )
        return {'id': request.id}

    @session_required(permissions=['requests'])
    async def update_confirmation(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        request = await RequestRepository().get_by_id(id_=id_)
        next_state = RequestStates.INPUT_RESERVATION
        if request.type == RequestTypes.OUTPUT:
            next_state = RequestStates.OUTPUT_RESERVATION
        await wallet_check_permission(
            account=account,
            wallets=[request.wallet],
            exception=RequestStateNotPermission(
                kwargs={
                    'id_value': request.id,
                    'action': f'Update state to {next_state}',
                }
            )
        )
        if request.state != RequestStates.WAITING:
            raise RequestStateWrong(
                kwargs={
                    'id_value': request.id,
                    'state': request.state,
                    'need_state': RequestStates.WAITING,
                },
            )
        await RequestRepository().update(request, state=next_state)
        await self.create_action(
            model=request,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'state': next_state,
            },
        )
        return {}
