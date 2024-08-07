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

from app.services.account_client_text import AccountClientTextService
from app.utils import Router
from app.utils.response import Response


router = Router(
    prefix='/get',
)


class AccountClientTextGetSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    key: str = Field(min_length=1, max_length=128)


@router.get()
async def route(schema: AccountClientTextGetSchema = Depends()):
    result = await AccountClientTextService().get(
        token=schema.token,
        key=schema.key,
    )
    return Response(**result)
