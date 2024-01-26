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


from pydantic import Field, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo

from app.db.models import RequisiteTypes
from app.services import RequisiteService
from app.utils import Router, Response, BaseSchema
from app.utils.base_schema import ValueMustBePositive
from app.utils.exaptions.main import DataValidationError

router = Router(
    prefix='/create',
)


class RequisiteCreateSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    type: str = Field(min_length=1, max_length=8)
    wallet_id: int = Field()
    output_requisite_data_id: int = Field(default=None)
    input_method_id: int = Field(default=None)
    total_currency_value: int = Field(default=None)
    currency_value_min: int = Field(default=None)
    currency_value_max: int = Field(default=None)
    rate: int = Field(default=None)
    total_value: int = Field(default=None)
    value_min: int = Field(default=None)
    value_max: int = Field(default=None)

    @field_validator('total_currency_value', 'rate', 'total_value')
    @classmethod
    def requisite_check_int(cls, value: int, info: ValidationInfo):
        if value is None:
            return
        if value <= 0:
            raise ValueMustBePositive(f'The field "{info.field_name}" must be positive')
        return value

    @model_validator(mode='after')
    def check_type(self) -> 'RequisiteCreateSchema':
        if self.type not in RequisiteTypes.choices:
            raise DataValidationError(f'The "type" must contain: {"/".join(RequisiteTypes.choices)}')

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
        if None in datas[self.type]['required']:
            raise DataValidationError(f'For {self.type}, only these parameters are taken into account: '
                                      f'{", ".join(datas[self.type]["required_names"])}')

        value_optional = [self.total_currency_value, self.total_value, self.rate]
        value_optional_names = ['total_currency_value', 'total_value', 'rate']
        if (len(value_optional) - value_optional.count(None)) != 2:
            raise DataValidationError(f'The position must be two of: {"/".join(value_optional_names)}')
        return self


@router.post()
async def route(schema: RequisiteCreateSchema):
    result = await RequisiteService().create(
        token=schema.token,
        type_=schema.type,
        wallet_id=schema.wallet_id,
        output_requisite_data_id=schema.output_requisite_data_id,
        input_method_id=schema.input_method_id,
        total_currency_value=schema.total_currency_value,
        currency_value_min=schema.currency_value_min,
        currency_value_max=schema.currency_value_max,
        rate=schema.rate,
        total_value=schema.total_value,
        value_min=schema.value_min,
        value_max=schema.value_max,
    )

    return Response(**result)
