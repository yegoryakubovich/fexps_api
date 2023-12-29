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


from pydantic import Field, BaseModel

from app.services import MethodService
from app.utils import Router, Response


router = Router(
    prefix='/create',
)


class MethodCreateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    currency_id_str: str = Field(min_length=2, max_length=32)
    name_text_key: str = Field(min_length=2, max_length=128)
    schema_fields: list[dict] = Field(default=[{"key": "string", "type": "string", "name": "string"}])


@router.post()
async def route(schema: MethodCreateSchema):
    result = await MethodService().create(
        token=schema.token,
        currency_id_str=schema.currency_id_str,
        name_text_key=schema.name_text_key,
        schema_fields=schema.schema_fields,
    )
    return Response(**result)
