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


from fastapi import Depends
from pydantic import Field, BaseModel

from app.services import OrderService
from app.utils import Response, Router


router = Router(
    prefix='/main',
)


class OrderListGetSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    by_request: bool = Field(default=False)
    by_requisite: bool = Field(default=False)
    is_active: bool = Field(default=False)
    is_finished: bool = Field(default=False)


@router.get()
async def route(schema: OrderListGetSchema = Depends()):
    result = await OrderService().get_all(
        token=schema.token,
        by_request=schema.by_request,
        by_requisite=schema.by_requisite,
        is_active=schema.is_active,
        is_finished=schema.is_finished,
    )
    return Response(**result)
