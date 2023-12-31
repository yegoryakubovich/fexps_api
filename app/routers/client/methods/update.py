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


from pydantic import Field

from app.services import MethodService
from app.utils import BaseSchema
from app.utils import Response, Router


router = Router(
    prefix='/update',
)


class MethodUpdateSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    id: int = Field()
    currency_id_str: str = Field(default=None, min_length=2, max_length=32)
    schema_fields: list[dict] = Field(default=None)


@router.post()
async def route(schema: MethodUpdateSchema):
    result = await MethodService().update(
        token=schema.token,
        id_=schema.id,
        currency_id_str=schema.currency_id_str or None,
        schema_fields=schema.schema_fields or None,
    )
    return Response(**result)
