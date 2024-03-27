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
            currency_id_str: str = None,
            schema_fields: list[dict] = None,
            schema_input_fields: list[dict] = None,
            color: str = None,
            bgcolor: str = None,
    ) -> None:
        updates = {}
        if currency_id_str:
            currency = await CurrencyRepository().get_by_id_str(id_str=currency_id_str)
            updates['currency'] = currency
        if schema_fields:
            for field in schema_fields:
                name_text = await TextRepository().create(
                    key=f'method_field_{await create_id_str()}',
                    value_default=field.get('name'),
                )
                field['name_text_key'] = name_text.key
            updates['schema_fields'] = schema_fields
        if schema_input_fields:
            for field in schema_fields:
                name_text = await TextRepository().create(
                    key=f'method_input_field_{await create_id_str()}',
                    value_default=field.get('name'),
                )
                field['name_text_key'] = name_text.key
            updates['schema_input_fields'] = schema_input_fields
        if color:
            updates['color'] = color
        if bgcolor:
            updates['bgcolor'] = bgcolor
        if not updates:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': ['currency_id_str', 'schema_fields', 'schema_input_fields'],
                },
            )
        await self.update(db_obj, **updates)
