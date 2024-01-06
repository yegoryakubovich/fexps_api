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


from pydantic import Field

from app.services import CountryService
from app.utils import BaseSchema
from app.utils import Router, Response


router = Router(
    prefix='/update',
)


class CountryUpdateSchema(BaseSchema):
    token: str = Field(min_length=32, max_length=64)
    id_str: str = Field(min_length=2, max_length=16)
    language: str = Field(default=None, min_length=2, max_length=16)
    timezone: str = Field(default=None, min_length=2, max_length=16)
    currency: str = Field(default=None, min_length=2, max_length=16)


@router.post()
async def route(schema: CountryUpdateSchema):
    result = await CountryService().update(
        token=schema.token,
        id_str=schema.id_str,
        language=schema.language,
        timezone=schema.timezone,
        currency=schema.currency,
    )
    return Response(**result)