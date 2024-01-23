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
    requisite_data_id: int = Field()
    total_currency_value: int = Field(default=None)
    total_currency_value_min: int = Field(default=None)
    total_currency_value_max: int = Field(default=None)
    rate: int = Field(default=None)
    total_value: int = Field(default=None)
    total_value_min: int = Field(default=None)
    total_value_max: int = Field(default=None)

    @field_validator('total_currency_value', 'rate', 'total_value')
    @classmethod
    def requisite_check_int(cls, value: int, info: ValidationInfo):
        if value is None:
            return
        if value <= 0:
            raise ValueMustBePositive(f'The field "{info.field_name}" must be positive')
        return value

    @field_validator('type')
    @classmethod
    def type_select(cls, type_, info: ValidationInfo):
        if type_ not in RequisiteTypes.choices:
            raise DataValidationError(f'The "{info.field_name}" must contain: {"/".join(RequisiteTypes.choices)}')
        return type_

    @model_validator(mode='after')
    def check_type(self) -> 'RequisiteCreateSchema':
        optional = [self.total_currency_value, self.total_value, self.rate]
        optional_names = ['total_currency_value', 'total_value', 'rate']

        if (len(optional) - optional.count(None)) != 2:
            raise DataValidationError(f'The position must be two of: {"/".join(optional_names)}')
        return self


@router.post()
async def route(schema: RequisiteCreateSchema):
    result = await RequisiteService().create(
        token=schema.token,
        type_=schema.type,
        wallet_id=schema.wallet_id,
        requisite_data_id=schema.requisite_data_id,
        total_currency_value=schema.total_currency_value,
        total_currency_value_min=schema.total_currency_value_min,
        total_currency_value_max=schema.total_currency_value_max,
        rate=schema.rate,
        total_value=schema.total_value,
        total_value_min=schema.total_value_min,
        total_value_max=schema.total_value_max,
    )

    return Response(**result)
