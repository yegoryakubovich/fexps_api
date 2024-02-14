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


from pydantic import Field, model_validator, field_validator, BaseModel
from pydantic_core.core_schema import ValidationInfo

from app.db.models import OrderRequestTypes
from app.services import OrderRequestService
from app.utils import Router, Response
from app.utils.exceptions.main import ValueMustBePositive, ParameterContainError

router = Router(
    prefix='/create',
)


class OrderRequestCreateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    order_id: int = Field()
    type: str = Field(min_length=1, max_length=16)
    value: int = Field(default=None)

    @model_validator(mode='after')
    def check_type(self) -> 'OrderRequestCreateSchema':
        if self.type not in OrderRequestTypes.choices:
            raise ParameterContainError(
                kwargs={
                    'field_name': 'type',
                    'parameters': OrderRequestTypes.choices,
                },
            )
        return self

    @field_validator('value')
    @classmethod
    def check_values(cls, value: int, info: ValidationInfo):
        if value is None:
            return
        if value <= 0:
            raise ValueMustBePositive(kwargs={'field_name': info.field_name})
        return value


@router.post()
async def route(schema: OrderRequestCreateSchema):
    result = await OrderRequestService().create(
        token=schema.token,
        order_id=schema.order_id,
        type_=schema.type,
        value=schema.value,
    )
    return Response(**result)
