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


from typing import Optional

from pydantic import Field, BaseModel

from app.services.requisite_data import RequisiteDataService
from app.utils import Router, Response


router = Router(
    prefix='/create',
)


class RequisiteDataCreateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    name: Optional[str] = Field(default=None)
    method_id: int = Field()
    fields: dict = Field()
    is_disposable: bool = Field(default=False)


@router.post()
async def route(schema: RequisiteDataCreateSchema):
    result = await RequisiteDataService().create(
        token=schema.token,
        name=schema.name,
        method_id=schema.method_id,
        fields=schema.fields,
        is_disposable=schema.is_disposable,
    )
    return Response(**result)
