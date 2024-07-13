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
import logging
from typing import Optional

from app.db.models import Method, Session, Actions, MethodFieldTypes, RequisiteTypes, RequisiteStates
from app.repositories import TextPackRepository, CurrencyRepository, MethodRepository, TextRepository, \
    RequisiteRepository
from app.services.base import BaseService
from app.services.currency import CurrencyService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required
from app.utils.exceptions import MethodFieldsParameterMissing, MethodFieldsTypeError
from app.utils.exceptions.method import MethodFieldsMissing


class MethodService(BaseService):
    model = Method

    @session_required(permissions=['methods'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            currency_id_str: str,
            name: str,
            fields: list[dict],
            input_fields: list[dict],
            input_rate_default: int,
            output_rate_default: int,
            input_rate_percent: int,
            output_rate_percent: int,
            color: str,
            bgcolor: str,
            is_rate_default: bool = None,
    ) -> dict:
        # fields
        if isinstance(fields, str):
            raise MethodFieldsMissing(kwargs={'field_name': 'fields'})
        for field in fields:
            name_text = await TextRepository().create(
                key=f'method_field_{await create_id_str()}',
                value_default=field.get('name'),
            )
            field['name_text_key'] = name_text.key
        # input_fields
        if isinstance(input_fields, str):
            raise MethodFieldsMissing(kwargs={'field_name': 'input_fields'})
        for input_field in input_fields:
            name_text = await TextRepository().create(
                key=f'method_input_fields_{await create_id_str()}',
                value_default=input_field.get('name'),
            )
            input_field['name_text_key'] = name_text.key
        currency = await CurrencyRepository().get_by_id_str(id_str=currency_id_str)
        name_text = await TextRepository().create(
            key=f'method_{await create_id_str()}',
            value_default=name,
        )
        method = await MethodRepository().create(
            currency=currency,
            name_text=name_text,
            schema_fields=fields,
            schema_input_fields=input_fields,
            input_rate_default=input_rate_default,
            output_rate_default=output_rate_default,
            input_rate_percent=input_rate_percent,
            output_rate_percent=output_rate_percent,
            color=color,
            bgcolor=bgcolor,
            is_rate_default=is_rate_default,
        )
        await TextPackRepository().create_all()
        await self.create_action(
            model=method,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'name_text': name_text.key,
                'currency': currency.id_str,
                'input_rate_default': input_rate_default,
                'output_rate_default': output_rate_default,
                'input_rate_percent': input_rate_percent,
                'output_rate_percent': output_rate_percent,
                'color': color,
                'bgcolor': bgcolor,
                'is_rate_default': is_rate_default,
            },
        )
        return {
            'id': method.id,
        }

    async def get(self, id_: int) -> dict:
        method = await MethodRepository().get_by_id(id_=id_)
        return {
            'method': await self.generate_method_dict(method=method)
        }

    async def get_list(self) -> dict:
        return {
            'methods': [
                await self.generate_method_dict(method=method)
                for method in await MethodRepository().get_list()
            ],
        }

    @session_required(permissions=['methods'], can_root=True)
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            currency: str = None,
            name: str = None,
            fields: list[dict] = None,
            input_fields: list[dict] = None,
            input_rate_default: int = None,
            output_rate_default: int = None,
            input_rate_percent: int = None,
            output_rate_percent: int = None,
            color: str = None,
            bgcolor: str = None,
            is_rate_default: bool = None,
    ) -> dict:
        method = await MethodRepository().get_by_id(id_=id_)
        await MethodRepository().update_method(
            method,
            currency=currency,
            name=name,
            schema_fields=fields,
            schema_input_fields=input_fields,
            input_rate_default=input_rate_default,
            output_rate_default=output_rate_default,
            input_rate_percent=input_rate_percent,
            output_rate_percent=output_rate_percent,
            color=color,
            bgcolor=bgcolor,
            is_rate_default=is_rate_default,
        )
        await TextPackRepository().create_all()
        action_parameters = {
            'updater': f'session_{session.id}',
            'id': id_,
        }
        if currency:
            action_parameters['currency'] = currency
        if name:
            action_parameters['name'] = name
        if fields:
            action_parameters['schema_fields'] = fields
        if input_fields:
            action_parameters['schema_input_fields'] = input_fields
        if input_rate_default:
            action_parameters['input_rate_default'] = input_rate_default
        if output_rate_default:
            action_parameters['output_rate_default'] = output_rate_default
        if input_rate_percent:
            action_parameters['input_rate_percent'] = input_rate_percent
        if output_rate_percent:
            action_parameters['output_rate_percent'] = output_rate_percent
        if color:
            action_parameters['color'] = color
        if bgcolor:
            action_parameters['bgcolor'] = bgcolor
        if is_rate_default:
            action_parameters['is_rate_default'] = is_rate_default
        await self.create_action(
            model=method,
            action=Actions.UPDATE,
            parameters=action_parameters,
        )
        return {}

    @session_required(permissions=['methods'], can_root=True)
    async def delete_by_admin(
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
            },
        )
        return {}

    @staticmethod
    async def generate_method_dict(method: Method) -> Optional[dict]:
        if not method:
            return
        input_requisites_sum = sum([
            requisite.currency_value
            for requisite in await RequisiteRepository().get_list(
                type=RequisiteTypes.OUTPUT,
                output_method=method,
                state=RequisiteStates.ENABLE,
            )
        ])
        output_requisites_sum = sum([
            requisite.currency_value
            for requisite in await RequisiteRepository().get_list(
                type=RequisiteTypes.INPUT,
                input_method=method,
                state=RequisiteStates.ENABLE,
            )
        ])
        logging.critical([
            requisite.currency_value
            for requisite in await RequisiteRepository().get_list(
                type=RequisiteTypes.INPUT,
                input_method=method,
                state=RequisiteStates.ENABLE,
            )
        ])
        return {
            'id': method.id,
            'currency': await CurrencyService().generate_currency_dict(currency=method.currency),
            'name_text': method.name_text.key,
            'schema_fields': method.schema_fields,
            'schema_input_fields': method.schema_input_fields,
            'input_rate_default': method.input_rate_default,
            'output_rate_default': method.output_rate_default,
            'input_rate_percent': method.input_rate_percent,
            'output_rate_percent': method.output_rate_percent,
            'color': method.color,
            'bgcolor': method.bgcolor,
            'input_requisites_sum': input_requisites_sum,
            'output_requisites_sum': output_requisites_sum,
            'is_rate_default': method.is_rate_default,
            'is_active': method.is_active,
        }

    @staticmethod
    async def method_check_validation_scheme(method: Method, fields: dict):
        for field in method.schema_fields:
            field_key = field.get('key')
            field_type = field.get('type')
            field_optional = field.get('optional')
            field_result = fields.get(field_key)
            if not field_result and field_optional:
                continue
            if not field_result:
                raise MethodFieldsParameterMissing(
                    kwargs={
                        'field_name': 'fields',
                        'parameter': field_key,
                    },
                )
            if field_type == MethodFieldTypes.STR and not isinstance(field_result, str):
                raise MethodFieldsTypeError(
                    kwargs={
                        'field_name': 'fields',
                        'param_name': field_key,
                        'type_name': field_type,
                    },
                )
            if field_type == MethodFieldTypes.INT and not isinstance(field_result, int):
                raise MethodFieldsTypeError(
                    kwargs={
                        'field_name': 'fields',
                        'param_name': field_key,
                        'type_name': field_type,
                    },
                )

    @staticmethod
    async def check_input_field(schema_input_fields: list, fields: dict):
        for field in schema_input_fields:
            field_key = field.get('key')
            field_type = field.get('type')
            field_optional = field.get('optional')
            field_result = fields.get(field_key)
            if not field_result and field_optional:
                continue
            if not field_result:
                raise MethodFieldsParameterMissing(
                    kwargs={
                        'field_name': 'fields',
                        'parameter': field_key,
                    },
                )
            for type_, python_type in [
                (MethodFieldTypes.STR, str),
                (MethodFieldTypes.INT, int),
                (MethodFieldTypes.IMAGE, str),
            ]:
                if field_type == type_ and not isinstance(field_result, python_type):
                    raise MethodFieldsTypeError(
                        kwargs={
                            'field_name': 'fields',
                            'param_name': field_key,
                            'type_name': field_type,
                        },
                    )
