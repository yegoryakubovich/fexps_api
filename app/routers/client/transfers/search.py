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

from app.services.transfer import TransferService
from app.utils import Response, Router


router = Router(
    prefix='/search',
)


class TransferSearchSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    wallet_id: int = Field()
    is_sender: Optional[bool] = Field(default=True)
    is_receiver: Optional[bool] = Field(default=True)
    page: Optional[int] = Field(default=1)


@router.post()
async def route(schema: TransferSearchSchema):
    result = await TransferService().search(
        token=schema.token,
        wallet_id=schema.wallet_id,
        is_sender=schema.is_sender,
        is_receiver=schema.is_receiver,
        page=schema.page,
    )
    return Response(**result)
