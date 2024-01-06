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
from typing import Optional

from _decimal import Decimal

from pydantic import Field, field_validator

from app.db.models import RequisiteTypes
from app.repositories.base import DataValidationError
from app.services import RequisiteService
from app.utils import Router, Response, BaseSchema
from app.utils.base_schema import ValueMustBePositive

router = Router(
    prefix='/create',
)


class RequisiteCreateSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    type: str = Field(min_length=1, max_length=8)
    wallet_id: int = Field()
    requisite_data_id: int = Field()
    currency: str = Field(min_length=2, max_length=16)
    currency_value: Decimal = Field(default=None, decimal_places=2)
    rate: Decimal = Field(default=None, decimal_places=2)
    total_value: Decimal = Field(default=None, decimal_places=2)
    value_min: float = Field()
    value_max: float = Field()

    @field_validator('type')
    @classmethod
    def type_select(cls, type_):
        if type_ not in RequisiteTypes.choices:
            raise DataValidationError(f'The type parameter must contain: {"/".join(RequisiteTypes.choices)}')
        return type_

    @field_validator('currency_value')
    @classmethod
    def check_currency_value(cls, currency_value):
        if currency_value is None:
            return
        if currency_value <= 0:
            raise ValueMustBePositive('The value must be positive')
        return float(currency_value)

    @field_validator('rate')
    @classmethod
    def check_rate(cls, rate):
        if rate is None:
            return
        if rate <= 0:
            raise ValueMustBePositive('The value must be positive')
        return float(rate)

    @field_validator('total_value')
    @classmethod
    def check_total_value(cls, total_value):
        if total_value is None:
            return
        if total_value <= 0:
            raise ValueMustBePositive('The value must be positive')
        return float(total_value)


@router.post()
async def route(schema: RequisiteCreateSchema):
    result = await RequisiteService().create(
        token=schema.token,
        type_=schema.type,
        wallet_id=schema.wallet_id,
        requisite_data_id=schema.requisite_data_id,
        currency_id_str=schema.currency,
        currency_value=schema.currency_value,
        rate=schema.rate,
        total_value=schema.total_value,
        value_min=schema.value_min,
        value_max=schema.value_max,
    )
    return Response(**result)
