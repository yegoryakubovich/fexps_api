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


from app.db.models import Session, Requisite
from app.repositories.method import MethodRepository
from app.repositories.requisite import RequisiteRepository
from app.services import MethodService
from app.services.base import BaseService
from app.utils.decorators import session_required


class RequisiteService(BaseService):
    model = Requisite

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
        requisite = await RequisiteRepository().create(
            account=account,
            method=method,
            fields=fields
        )
        await self.create_action(
            model=method,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'method_id': f'{method.id}',
            },
        )
        return {'requisite_id': requisite.id}

    @session_required()
    async def get_list(
            self,
            session: Session,
    ) -> dict:
        account = session.account
        requisites = {
            'requisites': [
                {
                    'id': requisite.id,
                    'method_id': requisite.method.id,
                    'fields': requisite.fields,
                }
                for requisite in await RequisiteRepository().get_list(account=account)
            ],
        }
        return requisites

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int,
    ):
        account = session.account
        requisite = await RequisiteRepository().get_by_account_and_id(account=account, id_=id_)
        return {
            'requisite': {
                'id': requisite.id,
                'method_id': requisite.method.id,
                'fields': requisite.fields,
            }
        }

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        requisite = await RequisiteRepository().get_by_account_and_id(account=account, id_=id_)
        await RequisiteRepository().delete(requisite)
        await self.create_action(
            model=requisite,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )
        return {}