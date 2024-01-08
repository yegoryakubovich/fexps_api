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

from app.services import RequestService
from app.utils import Router, Response, BaseSchema
from app.utils.base_schema import ValueMustBePositive

router = Router(
    prefix='/create',

)


class RequestCreateSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    wallet_id: int = Field()
    input_method_id: int = Field(default=None)
    input_value: Decimal = Field(default=None, decimal_places=2)
    rate: Decimal = Field(decimal_places=2)
    output_method_id: int = Field()
    output_requisite_data_id: int = Field()
    output_value: Decimal = Field(default=None, decimal_places=2)

    @field_validator('input_value')
    @classmethod
    def check_input_value(cls, input_value):
        if input_value is None:
            return
        if input_value <= 0:
            raise ValueMustBePositive('The input_value must be positive')
        return float(input_value)

    @field_validator('rate')
    @classmethod
    def check_rate(cls, rate):
        if rate is None:
            return
        if rate <= 0:
            raise ValueMustBePositive('The rate must be positive')
        return float(rate)

    @field_validator('output_value')
    @classmethod
    def check_output_value(cls, output_value):
        if output_value is None:
            return
        if output_value <= 0:
            raise ValueMustBePositive('The output_value must be positive')
        return float(output_value)


@router.post()
async def route(schema: RequestCreateSchema):
    result = await RequestService().create(
        token=schema.token,
        wallet_id=schema.wallet_id,
        input_method_id=schema.input_method_id or None,
        input_value=schema.input_value or None,
        rate=schema.rate,
        output_method_id=schema.output_method_id,
        output_requisite_data_id=schema.output_requisite_data_id,
        output_value=schema.output_value or None,
    )
    return Response(**result)
