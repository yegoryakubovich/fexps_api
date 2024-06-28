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

from pydantic import Field, field_validator, model_validator, BaseModel
from pydantic_core.core_schema import ValidationInfo

from app.db.models import RequestTypes
from app.services.request import RequestService
from app.utils import Router, Response
from app.utils.exceptions.main import ParametersAllContainError
from app.utils.exceptions.main import ValueMustBePositive, ParameterContainError, ParameterOneContainError


router = Router(
    prefix='/create',
)


class RequestCreateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    wallet_id: int = Field()
    type_: str = Field(min_length=1, max_length=8)
    name: Optional[str] = Field(default=None, min_length=1, max_length=32)
    input_method_id: Optional[int] = Field(default=None)
    output_requisite_data_id: Optional[int] = Field(default=None)
    input_value: Optional[int] = Field(default=None)
    output_value: Optional[int] = Field(default=None)

    @model_validator(mode='after')
    def check_type(self) -> 'RequestCreateSchema':
        # check type
        if self.type_ not in RequestTypes.choices:
            raise ParameterContainError(
                kwargs={
                    'field_name': 'type_',
                    'parameters': RequestTypes.choices,
                },
            )
        # check value
        if [self.input_value, self.output_value].count(None) != 1:
            raise ParameterOneContainError(
                kwargs={
                    'parameters': ['input_value', 'output_value'],
                },
            )
        # check method and requisite data
        if self.type_ == RequestTypes.INPUT and [self.input_method_id].count(None):
            raise ParametersAllContainError(
                kwargs={
                    'parameters': ['input_method'],
                },
            )
        if self.type_ == RequestTypes.OUTPUT and [self.output_requisite_data_id].count(None):
            raise ParametersAllContainError(
                kwargs={
                    'parameters': ['output_requisite_data'],
                },
            )
        if self.type_ == RequestTypes.ALL and [self.input_method_id, self.output_requisite_data_id].count(None):
            raise ParametersAllContainError(
                kwargs={
                    'parameters': ['input_method', 'output_requisite_data'],
                },
            )
        return self

    @field_validator('input_value', 'output_value')
    @classmethod
    def check_values(cls, value: int, info: ValidationInfo):
        if value is None:
            return
        if value <= 0:
            raise ValueMustBePositive(
                kwargs={
                    'field_name': info.field_name,
                },
            )
        return value


@router.post()
async def route(schema: RequestCreateSchema):
    result = await RequestService().create(
        token=schema.token,
        wallet_id=schema.wallet_id,
        type_=schema.type_,
        name=schema.name,
        input_method_id=schema.input_method_id,
        output_requisite_data_id=schema.output_requisite_data_id,
        input_value=schema.input_value,
        output_value=schema.output_value,
    )
    return Response(**result)
