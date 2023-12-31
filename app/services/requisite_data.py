#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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


from app.db.models import Session, RequisiteData
from app.repositories.method import MethodRepository
from app.repositories.requisite_data import RequisiteDataRepository
from app.services import MethodService
from app.services.base import BaseService
from app.utils.decorators import session_required


class RequisiteDataService(BaseService):
    model = RequisiteData

    @session_required()
    async def create(
            self,
            session: Session,
            method_id: int,
            fields: dict,
    ) -> dict:
        account = session.account
        method = await MethodRepository().get_by_id(id_=method_id)
        await MethodService().check_validation_scheme(method=method, fields=fields)
        requisite_data = await RequisiteDataRepository().create(
            account=account,
            method=method,
            fields=fields
        )
        await self.create_action(
            model=method,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id': requisite_data.id,
                'method_id': method.id,
            },
        )

        return {'requisite_id': requisite_data.id}

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        requisite_data = await RequisiteDataRepository().get_by_account_and_id(account=account, id_=id_)

        return {
            'requisite_data': {
                'id': requisite_data.id,
                'method_id': requisite_data.method.id,
                'fields': requisite_data.fields,
            }
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
    ) -> dict:
        account = session.account

        return {
            'requisite_datas': [
                {
                    'id': requisite_data.id,
                    'method_id': requisite_data.method.id,
                    'fields': requisite_data.fields,
                }
                for requisite_data in await RequisiteDataRepository().get_list(account=account)
            ],
        }

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
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )

        return {}
