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


from pydantic import Field, model_validator

from app.db.models import OrderRequestTypes
from app.repositories.base import DataValidationError
from app.services import OrderRequestService
from app.utils import Router, Response, BaseSchema


router = Router(
    prefix='/create',
)


class OrderRequestCreateSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    order_id: int = Field()
    type: str = Field(min_length=1, max_length=16)
    canceled_reason: str = Field(default=None, min_length=1, max_length=512)

    @model_validator(mode='after')
    def check_type(self) -> 'OrderRequestCreateSchema':
        if self.type not in OrderRequestTypes.choices:
            raise DataValidationError(f'The type parameter must contain: {"/".join(OrderRequestTypes.choices)}')

        if self.type == OrderRequestTypes.CANCEL:
            required = [self.canceled_reason]
            required_names = ['canceled_reason']
            if None in required:
                raise DataValidationError(
                    f'For {self.type}, only these parameters are taken into account: '
                    f'{", ".join(required_names)}'
                )


@router.post()
async def route(schema: OrderRequestCreateSchema):
    result = await OrderRequestService().create(
        token=schema.token,
        order_id=schema.order_id,
        type_=schema.type,
        canceled_reason=schema.canceled_reason,
    )
    return Response(**result)
