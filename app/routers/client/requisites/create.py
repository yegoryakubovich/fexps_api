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

from pydantic import Field, BaseModel, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo

from app.db.models import RequisiteTypes
from app.services.requisite import RequisiteService
from app.utils import Router, Response
from app.utils.exceptions.main import ValueMustBePositive, ParameterContainError, ParametersAllContainError, \
    ParameterTwoContainError


router = Router(
    prefix='/create',
)


class RequisiteCreateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    wallet_id: int = Field()
    type_: str = Field(min_length=1, max_length=8)
    output_requisite_data_id: Optional[int] = Field(default=None)
    input_method_id: Optional[int] = Field(default=None)
    currency_value: Optional[int] = Field(default=None)
    rate: Optional[int] = Field(default=None)
    value: Optional[int] = Field(default=None)
    currency_value_min: Optional[int] = Field(default=None)
    currency_value_max: Optional[int] = Field(default=None)
    is_flex: bool = Field(default=False)

    @field_validator('currency_value', 'rate', 'value', 'currency_value_min', 'currency_value_max')
    @classmethod
    def requisite_check_int(cls, value: int, info: ValidationInfo):
        if value is None:
            return
        if value <= 0:
            raise ValueMustBePositive(
                kwargs={
                    'field_name': info.field_name,
                },
            )
        return value

    @model_validator(mode='after')
    def check_type(self) -> 'RequisiteCreateSchema':
        if self.type_ not in [RequisiteTypes.INPUT, RequisiteTypes.OUTPUT]:
            raise ParameterContainError(
                kwargs={
                    'field_name': 'type_',
                    'parameters': [RequisiteTypes.INPUT, RequisiteTypes.OUTPUT],
                },
            )

        datas = {
            RequisiteTypes.INPUT: {
                'required': [self.input_method_id],
                'required_names': ['input_method_id'],
            },
            RequisiteTypes.OUTPUT: {
                'required': [self.output_requisite_data_id],
                'required_names': ['output_requisite_data_id'],
            },
        }
        if None in datas[self.type_]['required']:
            raise ParametersAllContainError(
                kwargs={
                    'parameters': datas[self.type_]["required_names"],
                },
            )
        value_optional = [self.currency_value, self.value, self.rate]
        value_optional_names = ['currency_value', 'value', 'rate']
        if self.is_flex:
            if (len(value_optional) - value_optional.count(None)) != 1:
                raise ParameterTwoContainError(kwargs={'parameters': value_optional_names})
        else:
            if (len(value_optional) - value_optional.count(None)) != 2:
                raise ParameterTwoContainError(kwargs={'parameters': value_optional_names})
        return self


@router.post()
async def route(schema: RequisiteCreateSchema):
    result = await RequisiteService().create(
        token=schema.token,
        type_=schema.type_,
        wallet_id=schema.wallet_id,
        output_requisite_data_id=schema.output_requisite_data_id,
        input_method_id=schema.input_method_id,
        currency_value=schema.currency_value,
        rate=schema.rate,
        value=schema.value,
        currency_value_min=schema.currency_value_min,
        currency_value_max=schema.currency_value_max,
        is_flex=schema.is_flex,
    )
    return Response(**result)
