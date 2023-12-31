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

from app.services import TransferService
from app.utils import Router, Response, BaseSchema
from app.utils.base_schema import ValueMustBePositive

router = Router(
    prefix='/create',
)


class TransferCreateSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    wallet_from_id: int = Field()
    wallet_to_id: int = Field()
    value: Decimal = Field(decimal_places=2)

    @field_validator('value')
    @classmethod
    def check_value(cls, value):
        if value is None:
            return
        if value <= 0:
            raise ValueMustBePositive('The value must be positive')
        return float(value)


@router.post()
async def route(schema: TransferCreateSchema):
    result = await TransferService().create(
        token=schema.token,
        wallet_from_id=schema.wallet_from_id,
        wallet_to_id=schema.wallet_to_id,
        value=schema.value,
    )
    return Response(**result)
