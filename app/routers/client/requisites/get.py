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


from fastapi import Depends
from pydantic import Field

from app.services.requisite import RequisiteService
from app.utils import Router, Response, BaseSchema

router = Router(
    prefix='/get',
)


class RequisiteGetSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    id: int = Field()


@router.get()
async def route(schema: RequisiteGetSchema = Depends()):
    result = await RequisiteService().get(
        token=schema.token,
        id_=schema.id,
    )
    return Response(**result)