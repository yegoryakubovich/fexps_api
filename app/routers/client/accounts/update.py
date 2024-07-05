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

from app.services import AccountService
from app.utils import Response, Router


router = Router(
    prefix='/update',
)


class AccountUpdateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    firstname: Optional[str] = Field(min_length=2, max_length=32, default=None)
    lastname: Optional[str] = Field(min_length=2, max_length=32, default=None)
    file_key: Optional[str] = Field(min_length=8, max_length=32, default=None)


@router.post()
async def route(schema: AccountUpdateSchema):
    result = await AccountService().update(
        token=schema.token,
        firstname=schema.firstname,
        lastname=schema.lastname,
        file_key=schema.file_key,
    )
    return Response(**result)
