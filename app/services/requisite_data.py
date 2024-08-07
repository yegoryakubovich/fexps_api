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

from app.db.models import Session, RequisiteData, Actions
from app.repositories import MethodRepository, RequisiteDataRepository, RequestRepository, RequisiteRepository
from app.services.base import BaseService
from app.services.currency import CurrencyService
from app.services.method import MethodService
from app.utils.decorators import session_required


class RequisiteDataService(BaseService):
    model = RequisiteData

    @session_required()
    async def create(
            self,
            session: Session,
            name: Optional[str],
            method_id: int,
            fields: dict,
            is_disposable: bool,
    ) -> dict:
        account = session.account
        if not name:
            name = None
        method = await MethodRepository().get_by_id(id_=method_id)
        await MethodService().method_check_validation_scheme(method=method, fields=fields)
        requisite_data = await RequisiteDataRepository().create(
            account=account,
            name=name,
            method=method,
            fields=fields,
            is_disposable=is_disposable,
        )
        await self.create_action(
            model=requisite_data,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'name': name,
                'method_id': method.id,
                'fields': fields,
                'is_disposable': is_disposable,
            },
        )
        return {
            'id': requisite_data.id,
        }

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        requisite_data = await RequisiteDataRepository().get_by_account_and_id(account=account, id_=id_)
        return {
            'requisite_data': await self.generate_requisite_data_dict(requisite_data=requisite_data),
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
    ) -> dict:
        account = session.account
        requisites_datas_list = []
        for requisite_data in await RequisiteDataRepository().get_list(account=account):
            requisites_datas_list.append(
                await self.generate_requisite_data_dict(requisite_data=requisite_data),
            )
        return {
            'requisite_datas': [
                await self.generate_requisite_data_dict(requisite_data=requisite_data)
                for requisite_data in await RequisiteDataRepository().get_list(account=account)
            ],
        }

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            fields: dict,
    ) -> dict:
        account = session.account
        requisite_data = await RequisiteDataRepository().get_by_id(id_=id_, account=account)
        await MethodService().method_check_validation_scheme(method=requisite_data.method, fields=fields)
        await RequisiteDataRepository().update(
            requisite_data,
            fields=fields,
        )
        await self.create_action(
            model=requisite_data,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'id': id_,
                'fields': fields,
            },
        )
        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        requisite_data = await RequisiteDataRepository().get_by_account_and_id(account=account, id_=id_)
        await RequisiteDataRepository().delete(requisite_data)
        await self.create_action(
            model=requisite_data,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
            },
        )
        return {}

    @staticmethod
    async def generate_requisite_data_dict(requisite_data: RequisiteData) -> Optional[dict]:
        if not requisite_data:
            return
        allow = True
        if requisite_data.is_disposable:
            if await RequestRepository().get(output_requisite_data=requisite_data):
                allow = False
            if await RequisiteRepository().get(output_requisite_data=requisite_data):
                allow = False
        name = requisite_data.name
        if not name:
            for key, value in requisite_data.fields.items():
                name = value
        return {
            'id': requisite_data.id,
            'account': requisite_data.account_id,
            'name': name,
            'method': await MethodService().generate_method_dict(method=requisite_data.method),
            'currency': await CurrencyService().generate_currency_dict(currency=requisite_data.method.currency),
            'fields': requisite_data.fields,
            'is_disposable': requisite_data.is_disposable,
            'allow': allow,
        }
