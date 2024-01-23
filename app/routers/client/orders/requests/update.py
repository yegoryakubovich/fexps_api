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


from pydantic import Field, model_validator

from app.db.models import OrderRequestStates
from app.services import OrderRequestService
from app.utils import BaseSchema
from app.utils import Response, Router
from app.utils.exaptions.main import DataValidationError

router = Router(
    prefix='/update',
)


class OrderRequestUpdateSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    id: int = Field()
    state: str = Field()

    @model_validator(mode='after')
    def check_type(self) -> 'OrderRequestUpdateSchema':
        if self.state not in OrderRequestStates.choices_update:
            raise DataValidationError(f'The type parameter must contain: {"/".join(OrderRequestStates.choices_update)}')
        return self


@router.post()
async def route(schema: OrderRequestUpdateSchema):
    result = await OrderRequestService().update(
        token=schema.token,
        id_=schema.id,
        state=schema.state,
    )

    return Response(**result)
