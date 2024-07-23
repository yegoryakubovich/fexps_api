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

from pydantic import Field, BaseModel, model_validator

from app.db.models import CommissionPackTelegramTypes
from app.services.commission_pack import CommissionPackService
from app.utils import Router, Response
from app.utils.exceptions import ParameterContainError


router = Router(
    prefix='/update',
)


class CommissionPackUpdateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id_: int = Field()
    name: str = Field(min_length=1, max_length=1024)
    telegram_chat_id: Optional[int] = Field(default=None)
    telegram_type: Optional[str] = Field(default=None, min_length=1, max_length=1024)
    is_default: bool = Field(default=False)

    @model_validator(mode='after')
    def check_scheme(self) -> 'CommissionPackUpdateSchema':
        if self.telegram_type not in [None, CommissionPackTelegramTypes.FEXPS, CommissionPackTelegramTypes.SOWAPAY]:
            raise ParameterContainError(
                kwargs={
                    'field_name': 'telegram_type',
                    'parameters': [CommissionPackTelegramTypes.FEXPS, CommissionPackTelegramTypes.SOWAPAY],
                },
            )
        return self


@router.post()
async def route(schema: CommissionPackUpdateSchema):
    result = await CommissionPackService().update_by_admin(
        token=schema.token,
        id_=schema.id_,
        name=schema.name,
        telegram_chat_id=schema.telegram_chat_id,
        telegram_type=schema.telegram_type,
        is_default=schema.is_default,
    )
    return Response(**result)
