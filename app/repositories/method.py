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


from app.db.models import Method
from app.repositories.base import BaseRepository
from app.repositories.currency import CurrencyRepository
from app.repositories.text import TextRepository
from app.utils.crypto import create_id_str
from app.utils.exceptions import NoRequiredParameters


class MethodRepository(BaseRepository[Method]):
    model = Method

    async def update_method(
            self,
            db_obj: Method,
            currency: str = None,
            name: str = None,
            schema_fields: list[dict] = None,
            schema_input_fields: list[dict] = None,
            input_rate_default: int = None,
            output_rate_default: int = None,
            input_rate_percent: int = None,
            output_rate_percent: int = None,
            color: str = None,
            bgcolor: str = None,
            is_rate_default: bool = None,
    ) -> None:
        updates = {}
        if currency:
            updates['currency'] = await CurrencyRepository().get_by_id_str(id_str=currency)
        if name:
            a = await TextRepository().update(db_obj.name_text, value_default=name)
        if schema_fields:
            for field in schema_fields:
                name_text = await TextRepository().create(
                    key=f'method_field_{await create_id_str()}',
                    value_default=field.get('name'),
                )
                field['name_text_key'] = name_text.key
            updates['schema_fields'] = schema_fields
        if schema_input_fields:
            for field in schema_input_fields:
                name_text = await TextRepository().create(
                    key=f'method_input_field_{await create_id_str()}',
                    value_default=field.get('name'),
                )
                field['name_text_key'] = name_text.key
            updates['schema_input_fields'] = schema_input_fields
        if input_rate_default is not None:
            updates['input_rate_default'] = input_rate_default
        if output_rate_default is not None:
            updates['output_rate_default'] = output_rate_default
        if input_rate_percent is not None:
            updates['input_rate_percent'] = input_rate_percent
        if output_rate_percent is not None:
            updates['output_rate_percent'] = output_rate_percent
        if color is not None:
            updates['color'] = color
        if bgcolor is not None:
            updates['bgcolor'] = bgcolor
        if is_rate_default is not None:
            updates['is_rate_default'] = is_rate_default
        if not updates:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': ['currency_id_str', 'schema_fields', 'schema_input_fields'],
                },
            )
        await self.update(db_obj, **updates)
