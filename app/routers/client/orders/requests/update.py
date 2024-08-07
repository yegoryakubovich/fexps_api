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


from pydantic import Field, BaseModel, model_validator

from app.db.models import OrderRequestStates
from app.services.order_request import OrderRequestService
from app.utils import Response, Router
from app.utils.exceptions.main import ParameterContainError


router = Router(
    prefix='/update',
)


class OrderRequestUpdateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id_: int = Field()
    state: str = Field()

    @model_validator(mode='after')
    def check_type(self) -> 'OrderRequestUpdateSchema':
        if self.state not in [OrderRequestStates.CANCELED, OrderRequestStates.COMPLETED]:
            raise ParameterContainError(
                kwargs={
                    'field_name': 'state',
                    'parameters': [OrderRequestStates.CANCELED, OrderRequestStates.COMPLETED],
                },
            )
        return self


@router.post()
async def route(schema: OrderRequestUpdateSchema):
    result = await OrderRequestService().update(
        token=schema.token,
        id_=schema.id_,
        state=schema.state,
    )
    return Response(**result)
