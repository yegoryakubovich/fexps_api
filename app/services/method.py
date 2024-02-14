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


from app.db.models import Method, Session, Actions
from app.repositories.currency import CurrencyRepository
from app.repositories.method import MethodRepository
from app.repositories.text import TextRepository
from app.services.base import BaseService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required
from app.utils.exceptions.method import MethodFieldsMissing


class MethodService(BaseService):
    model = Method

    @session_required(permissions=['methods'])
    async def create(
            self,
            session: Session,
            currency_id_str: str,
            name: str,
            fields: list[dict],
            confirmation_fields: list[dict],
    ) -> dict:
        if isinstance(fields, str):
            raise MethodFieldsMissing(kwargs={'field_name': 'fields'})
        for field in fields:
            name_text = await TextRepository().create(
                key=f'method_field_{await create_id_str()}',
                value_default=field.get('name'),
            )
            field['name_text_key'] = name_text.key
        if isinstance(confirmation_fields, str):
            raise MethodFieldsMissing(kwargs={'field_name': 'confirmation_fields'})
        for confirmation_field in confirmation_fields:
            name_text = await TextRepository().create(
                key=f'method_confirmation_field_{await create_id_str()}',
                value_default=confirmation_field.get('name'),
            )
            confirmation_field['name_text_key'] = name_text.key

        currency = await CurrencyRepository().get_by_id_str(id_str=currency_id_str)
        name_text = await TextRepository().create(
            key=f'method_{await create_id_str()}',
            value_default=name,
        )
        method = await MethodRepository().create(
            currency=currency,
            name_text=name_text,
            schema_fields=fields,
            schema_confirmation_fields=confirmation_fields
        )
        await self.create_action(
            model=method,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'name_text': name_text.key,
                'currency': currency.id_str
            },
        )
        return {'method_id': method.id}

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
                'schema_input_fields': method.schema_confirmation_fields,
                'is_active': method.is_active,
            }
        }

    @staticmethod
    async def get_list() -> dict:
        return {
            'methods': [
                {
                    'id': method.id,
                    'currency_id_str': method.currency.id_str,
                    'name_text_key': method.name_text.key,
                    'schema_fields': method.schema_fields,
                    'schema_input_fields': method.schema_confirmation_fields,
                    'is_active': method.is_active,
                }
                for method in await MethodRepository().get_list()
            ],
        }

    @session_required(permissions=['methods'])
    async def update(
            self,
            session: Session,
            id_: int,
            currency_id_str: str = None,
            schema_fields: list = None,
    ) -> dict:
        text = await MethodRepository().get_by_id(id_=id_)
        await MethodRepository().update_method(
            text,
            currency_id_str=currency_id_str,
            schema_fields=schema_fields,
        )
        action_parameters = {
            'updater': f'session_{session.id}',
            'id': id_,
        }
        if currency_id_str:
            action_parameters['currency_id_str'] = currency_id_str
        if schema_fields:
            action_parameters['schema_fields'] = schema_fields
        await self.create_action(
            model=text,
            action=Actions.UPDATE,
            parameters=action_parameters,
        )
        return {}

    @session_required(permissions=['methods'])
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        method = await MethodRepository().get(id=id_)
        await MethodRepository().delete(method)
        await self.create_action(
            model=method,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )
        return {}
