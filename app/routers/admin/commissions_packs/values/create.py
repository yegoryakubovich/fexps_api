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


from pydantic import Field, model_validator, field_validator
from pydantic_core.core_schema import ValidationInfo

from app.services import CommissionPackValueService
from app.services.commission_pack_value import IntervalValidationError
from app.utils import BaseSchema
from app.utils import Router, Response
from app.utils.exaptions.main import DataValidationError


router = Router(
    prefix='/create',
)


class CommissionPackValueCreateSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    commission_pack_id: int = Field()
    value_from: int = Field()
    value_to: int = Field()
    percent: int = Field(default=None)
    value: int = Field(default=None)

    @model_validator(mode='after')
    def check_type(self) -> 'CommissionPackValueCreateSchema':
        if (self.value_from >= self.value_to) and (self.value_to != 0):
            raise IntervalValidationError(f'The field value_to must be greater than value_from')

        optional = [self.percent, self.value]
        optional_names = ['percent', 'value']

        if (len(optional) - optional.count(None)) < 1:
            raise DataValidationError(f'There must be at least one position: {"/".join(optional_names)}')

        return self

    @field_validator('value_from', 'value_to')
    @classmethod
    def check_value_interval(cls, value: int, info: ValidationInfo):
        if value < 0:
            raise IntervalValidationError(f'The field "{info.field_name}" must be positive')
        return value


@router.post()
async def route(schema: CommissionPackValueCreateSchema):
    result = await CommissionPackValueService().create(
        token=schema.token,
        commission_pack_id=schema.commission_pack_id,
        value_from=schema.value_from,
        value_to=schema.value_to,
        percent=schema.percent,
        value=schema.value,
    )

    return Response(**result)