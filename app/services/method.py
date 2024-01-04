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
from app.utils import ApiException
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required


class FieldsMissingParams(ApiException):
    pass


class FieldsValidationError(ApiException):
    pass


class MethodFieldType:
    str = 'str'
    int = 'int'


class MethodService(BaseService):
    model = Method

    @staticmethod
    async def check_validation_fields(fields: list[dict]) -> None:
        for i, field in enumerate(fields, start=1):
            for key in ['key', 'type', 'name']:
                if not field.get(key):
                    raise FieldsMissingParams(f'fields.{i} missing parameter "{key}"')
            if field.get('type') not in [MethodFieldType.str, MethodFieldType.int]:
                raise FieldsValidationError(f'fields.{i}.type must contain {MethodFieldType.str}/{MethodFieldType.int}')

    @staticmethod
    async def check_validation_scheme(method: Method, fields: dict):
        for field in method.schema_fields:
            field_key = field.get('key')
            field_type = field.get('type')
            field_result = fields.get(field_key)
            if not field_result:
                raise FieldsMissingParams(f'fields missing parameter "{field_key}"')
            if field_type == MethodFieldType.str and not isinstance(field_result, str):
                raise FieldsValidationError(f'fields.{field_key} does not match {field_type}')
            if field_type == MethodFieldType.int and not isinstance(field_result, int):
                raise FieldsValidationError(f'fields.{field_key} does not match {field_type}')

    @session_required()
    async def create(
            self,
            session: Session,
            currency_id_str: str,
            name: str,
            fields: list[dict],
    ) -> dict:
        await self.check_validation_fields(fields=fields)
        for field in fields:
            name_text = await TextRepository().create(
                key=f'method_field_{await create_id_str()}',
                value_default=field.get('name'),
            )
            field['name_text_key'] = name_text.key
        currency = await CurrencyRepository().get_by_id_str(id_str=currency_id_str)
        name_text = await TextRepository().create(
            key=f'method_{await create_id_str()}',
            value_default=name,
        )
        method = await MethodRepository().create(
            currency=currency,
            name_text=name_text,
            schema_fields=fields
        )
        await self.create_action(
            model=method,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'name_text_id': name_text.id,
                'currency_id_str': currency.id_str
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
            action='update',
            parameters=action_parameters,
        )
        return {}
