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

from datetime import datetime

from pydantic import BaseModel, Field

from app.services import AccountServiceService
from app.utils import Response, Router


router = Router(
    prefix='/update',
)


class AccountServiceUpdateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id: int = Field()
    answers: str = Field(default=None, min_length=2, max_length=8192)
    state: str = Field(default=None, min_length=2, max_length=128)
    datetime_from: datetime = Field(default=None)
    datetime_to: datetime = Field(default=None)


@router.post()
async def route(schema: AccountServiceUpdateByAdminSchema):
    result = await AccountServiceService().update_by_admin(
        token=schema.token,
        id_=schema.id,
        answers=schema.answers,
        state=schema.state,
        datetime_from=schema.datetime_from,
        datetime_to=schema.datetime_to,
    )
    return Response(**result)
