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

from app.services import WalletService
from app.utils import Router, Response


router = Router(
    prefix='/create',
)


class WalletCreateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    name: str = Field(min_length=1, max_length=32, default='Wallet')


@router.post()
async def route(schema: WalletCreateSchema):
    result = await WalletService().create(
        token=schema.token,
        name=schema.name,
    )
    return Response(**result)
