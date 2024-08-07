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

from pydantic import Field, BaseModel

from app.services.order import OrderService
from app.utils import Response, Router


router = Router(
    prefix='/confirmation',
)


class OrderUpdateConfirmationSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id_: int = Field()
    rate: Optional[int] = Field(default=None)
    input_fields: dict = Field()


@router.post()
async def route(schema: OrderUpdateConfirmationSchema):
    result = await OrderService().update_confirmation(
        token=schema.token,
        id_=schema.id_,
        rate=schema.rate,
        input_fields=schema.input_fields,
    )
    return Response(**result)
