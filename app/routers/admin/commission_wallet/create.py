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


from pydantic import Field, model_validator

from app.repositories.base import DataValidationError
from app.services import CommissionWalletService
from app.utils import BaseSchema
from app.utils import Router, Response


router = Router(
    prefix='/create',
)


class CommissionWalletCreateSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    wallet_id: int = Field()
    percent: int = Field(default=None)
    value: int = Field(default=None)

    @model_validator(mode='after')
    def check_type(self) -> 'CommissionWalletCreateSchema':
        optional = [self.percent, self.value]
        optional_names = ['percent', 'value']
        if (len(optional) - optional.count(None)) != 1:
            raise DataValidationError(f'The position must be one of: {"/".join(optional_names)}')
        return self


@router.post()
async def route(schema: CommissionWalletCreateSchema):
    result = await CommissionWalletService().create(
        token=schema.token,
        wallet_id=schema.wallet_id,
        percent=schema.percent,
        value=schema.value,
    )
    return Response(**result)
