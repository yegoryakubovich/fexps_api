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

from pydantic import Field, field_validator, model_validator

from app.db.models import RequestTypes
from app.repositories.base import DataValidationError
from app.services import RequestService
from app.utils import Router, Response, BaseSchema
from app.utils.base_schema import ValueMustBePositive

router = Router(
    prefix='/create',

)


class RequestCreateSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    wallet_id: int = Field()
    type: str = Field(min_length=1, max_length=8)

    input_method_id: int = Field(default=None)
    input_value: Decimal = Field(default=None, decimal_places=2)

    value: Decimal = Field(default=None, decimal_places=2)

    output_method_id: int = Field(default=None)
    output_requisite_data_id: int = Field(default=None)
    output_value: Decimal = Field(default=None, decimal_places=2)

    @model_validator(mode='after')
    def check_type(self) -> 'RequestCreateSchema':
        if self.type not in RequestTypes.choices:
            raise DataValidationError(f'The type parameter must contain: {"/".join(RequestTypes.choices)}')
        datas = {
            RequestTypes.INPUT: {
                'variables': [self.input_method_id, self.input_value, self.value],
                'names': ['input_method_id', 'input_value', 'value']
            },
            RequestTypes.OUTPUT: {
                'variables': [self.output_requisite_data_id, self.output_method_id,
                              self.output_value, self.value],
                'names': ['output_requisite_data_id', 'output_method_id', 'output_value', 'value']
            },
            RequestTypes.ALL: {
                'variables': [self.input_method_id, self.input_value,
                              self.output_requisite_data_id,
                              self.output_method_id, self.output_value],
                'names': ['input_method_id', 'input_value', 'output_requisite_data_id',
                          'output_method_id', 'output_value']
            }
        }
        if None in datas[self.type]['variables']:
            raise DataValidationError(f'For {self.type}, only these parameters are taken into account: '
                                      f'{", ".join(datas[self.type]["names"])}')
        return self

    @field_validator('input_value', 'value', 'output_value')
    @classmethod
    def check_values(cls, value):
        if value is None:
            return
        if value <= 0:
            raise ValueMustBePositive(f'The number {value} must be positive')
        return float(value)


@router.post()
async def route(schema: RequestCreateSchema):
    result = await RequestService().create(
        token=schema.token,
        wallet_id=schema.wallet_id,
        type_=schema.type,
        input_method_id=schema.input_method_id or None,
        input_value=schema.input_value or None,
        value=schema.value or None,
        output_method_id=schema.output_method_id or None,
        output_requisite_data_id=schema.output_requisite_data_id or None,
        output_value=schema.output_value or None,
    )
    return Response(**result)
