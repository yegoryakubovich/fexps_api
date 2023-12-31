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


from decimal import Decimal

from pydantic import Field, field_validator

from app.services import RequisiteService
from app.utils import BaseSchema
from app.utils import Router, Response
from app.utils.base_schema import ValueMustBePositive


router = Router(
    prefix='/update',
)


class RequisiteUpdateSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    id: int = Field()
    total_value: Decimal = Field(decimal_places=2)

    @field_validator('total_value')
    @classmethod
    def check_total_value(cls, total_value):
        if total_value <= 0:
            raise ValueMustBePositive('The value must be positive')
        return float(total_value)


@router.post()
async def route(schema: RequisiteUpdateSchema):
    result = await RequisiteService().update(
        token=schema.token,
        id_=schema.id,
        total_value=schema.total_value,
    )
    return Response(**result)
