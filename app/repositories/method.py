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
from .base import BaseRepository
from .currency import CurrencyRepository
from app.utils.exaptions.main import NoRequiredParameters


class MethodRepository(BaseRepository[Method]):
    model = Method

    async def update_method(self, db_obj: Method,
                            currency_id_str: str = None, name_text_key: str = None, schema_fields: list = None):
        if currency_id_str:
            currency = await CurrencyRepository().get_by_id_str(id_str=currency_id_str)
            await self.update(db_obj, currency=currency)
        if schema_fields:
            await self.update(db_obj, schema_fields=schema_fields)
        if not currency_id_str and not name_text_key and not schema_fields:
            raise NoRequiredParameters(
                'One of the following parameters must be filled in: currency_id_str, name_text_key, schema_fields'
            )
