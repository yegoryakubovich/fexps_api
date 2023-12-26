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


from pydantic import Field, BaseModel

from app.services import MethodService
from app.utils import Router, Response


router = Router(
    prefix='/update',
)


class MethodCreateSchema(BaseModel):
    id: int = Field()
    is_active: bool = Field()


@router.post()
async def route(schema: MethodCreateSchema):
    result = await MethodService().update(
        token=schema.token,
        id_=schema.id,
        is_active=schema.is_active,
    )
    return Response(**result)
