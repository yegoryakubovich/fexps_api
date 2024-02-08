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


from pydantic import Field, BaseModel

from app.services import OrderStatesConfirmationService
from app.utils import Response, Router


router = Router(
    prefix='/update',
)


class OrderStatesConfirmationUpdateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    order_id: int = Field()
    confirmation_fields: dict = Field()


@router.post()
async def route(schema: OrderStatesConfirmationUpdateSchema):
    result = await OrderStatesConfirmationService().update(
        token=schema.token,
        id_=schema.order_id,
        confirmation_fields=schema.confirmation_fields,
    )
    return Response(**result)
