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
from app.repositories import TextPackRepository
from app.repositories.currency import CurrencyRepository
from app.repositories.method import MethodRepository
from app.repositories.text import TextRepository
from app.services import CurrencyService
from app.services.base import BaseService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required
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
            rate_input_default: int,
            rate_output_default: int,
            rate_input_percent: int,
            rate_output_percent: int,
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
            rate_input_default=rate_input_default,
            rate_output_default=rate_output_default,
            rate_input_percent=rate_input_percent,
            rate_output_percent=rate_output_percent,
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
                'rate_input_default': rate_input_default,
                'rate_output_default': rate_output_default,
                'rate_input_percent': rate_input_percent,
                'rate_output_percent': rate_output_percent,
                'color': color,
                'bgcolor': bgcolor,
                'is_rate_default': is_rate_default,
            },
        )
        return {'id': method.id}

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
            rate_input_default: int = None,
            rate_output_default: int = None,
            rate_input_percent: int = None,
            rate_output_percent: int = None,
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
            rate_input_default=rate_input_default,
            rate_output_default=rate_output_default,
            rate_input_percent=rate_input_percent,
            rate_output_percent=rate_output_percent,
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
        if rate_input_default:
            action_parameters['rate_input_default'] = rate_input_default
        if rate_output_default:
            action_parameters['rate_output_default'] = rate_output_default
        if rate_input_percent:
            action_parameters['rate_input_percent'] = rate_input_percent
        if rate_output_percent:
            action_parameters['rate_output_percent'] = rate_output_percent
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
                'id': id_,
            },
        )
        return {}

    @staticmethod
    async def generate_method_dict(method: Method) -> dict:
        return {
            'id': method.id,
            'currency': await CurrencyService().generate_currency_dict(currency=method.currency),
            'name_text': method.name_text.key,
            'schema_fields': method.schema_fields,
            'schema_input_fields': method.schema_input_fields,
            'rate_input_default': method.rate_input_default,
            'rate_output_default': method.rate_output_default,
            'rate_input_percent': method.rate_input_percent,
            'rate_output_percent': method.rate_output_percent,
            'color': method.color,
            'bgcolor': method.bgcolor,
            'is_rate_default': method.is_rate_default,
            'is_active': method.is_active,
        }
