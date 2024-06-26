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


from pydantic import BaseModel, Field

from app.services.country import CountryService
from app.utils import Router, Response


router = Router(
    prefix='/update',
)


class CountryUpdateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id_str: str = Field(min_length=1, max_length=16)
    language_default: str = Field(default=None, min_length=1, max_length=16)
    timezone_default: str = Field(default=None, min_length=1, max_length=16)
    currency_default: str = Field(default=None, min_length=1, max_length=16)


@router.post()
async def route(schema: CountryUpdateByAdminSchema):
    result = await CountryService().update_by_admin(
        token=schema.token,
        id_str=schema.id_str,
        language_default_id_str=schema.language_default,
        timezone_default_id_str=schema.timezone_default,
        currency_default_id_str=schema.currency_default,
    )
    return Response(**result)
