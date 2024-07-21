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

from app.services.account_client_text import AccountClientTextService
from app.utils import Response, Router


router = Router(
    prefix='/update',
)


class AccountClientTextUpdateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id_: int = Field()
    value: str = Field(min_length=1, max_length=2048)


@router.post()
async def route(schema: AccountClientTextUpdateSchema):
    result = await AccountClientTextService().update(
        token=schema.token,
        id_=schema.id_,
        value=schema.value,
    )
    return Response(**result)
