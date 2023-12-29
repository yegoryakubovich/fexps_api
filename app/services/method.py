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
from app.db.models import Method, Session
from app.repositories.currency import CurrencyRepository
from app.repositories.method import MethodRepository
from app.repositories.text import TextRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class MethodService(BaseService):
    model = Method

    @session_required()
    async def create(
            self,
            session: Session,
            currency_id_str: str,
            name_text_key: str,
            schema_fields: list[dict],
    ) -> dict:
        currency = await CurrencyRepository().get_by_id_str(id_str=currency_id_str)
        name_text = await TextRepository().get_by_key(key=name_text_key)
        method = await MethodRepository().create(
            currency=currency,
            name_text=name_text,
            schema_fields=schema_fields
        )
        await self.create_action(
            model=method,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
            },
        )
        return {'method_id': method.id}

    @staticmethod
    async def get_list() -> dict:
        methods = {
            'methods': [
                {
                    'id': method.id,
                    'currency_id_str': method.currency.id_str,
                    'name_text_key': method.name_text.key,
                    'schema_fields': method.schema_fields,
                    'is_active': method.is_active,
                }
                for method in await MethodRepository().get_list()
            ],
        }
        return methods

    @staticmethod
    async def get(
            id_: int,
    ):
        method = await MethodRepository().get_by_id(id_=id_)
        return {
            'method': {
                'id': method.id,
                'currency_id_str': method.currency.id_str,
                'name_text_key': method.name_text.key,
                'schema_fields': method.schema_fields,
                'is_active': method.is_active,
            }
        }

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        method = await MethodRepository().get(id=id_)
        await MethodRepository().delete(method)
        await self.create_action(
            model=method,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )
        return {}

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            currency_id_str: str = None,
            name_text_key: str = None,
            schema_fields: list = None,
    ) -> dict:
        text = await MethodRepository().get_by_id(id_=id_)
        await MethodRepository().update_method(
            text,
            currency_id_str=currency_id_str,
            name_text_key=name_text_key,
            schema_fields=schema_fields,
        )

        action_parameters = {
            'updater': f'session_{session.id}',
            'id': id_,
        }
        if currency_id_str:
            action_parameters['currency_id_str'] = currency_id_str
        if name_text_key:
            action_parameters['name_text_key'] = name_text_key
        if schema_fields:
            action_parameters['schema_fields'] = schema_fields
        await self.create_action(
            model=text,
            action='update',
            parameters=action_parameters,
        )
        return {}
