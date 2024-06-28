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


from pydantic import Field, BaseModel, field_validator
from pydantic_core.core_schema import ValidationInfo

from app.services.requisite import RequisiteService
from app.utils import Router, Response
from app.utils.exceptions.main import ValueMustBePositive


router = Router(
    prefix='/value',
)


class RequisiteUpdateValueSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id_: int = Field()
    currency_value: int = Field()

    @field_validator('currency_value')
    @classmethod
    def requisite_check_values(cls, value: int, info: ValidationInfo):
        if value is None:
            return
        if value <= 0:
            raise ValueMustBePositive(kwargs={'field_name': info.field_name})
        return value


@router.post()
async def route(schema: RequisiteUpdateValueSchema):
    result = await RequisiteService().update_value(
        token=schema.token,
        id_=schema.id_,
        total_currency_value=schema.currency_value,
    )
    return Response(**result)
