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


from typing import Optional

from pydantic import BaseModel, Field

from app.services import AccountService
from app.utils import Router, Response


router = Router(
    prefix='/create',
)


class CreateAccountSchema(BaseModel):
    username: str = Field(min_length=6, max_length=32)
    password: str = Field(min_length=6, max_length=128)
    firstname: str = Field(min_length=2, max_length=32)
    lastname: str = Field(min_length=2, max_length=32)
    surname: Optional[str] = Field(min_length=2, max_length=32, default=None)
    country: str = Field(max_length=16)
    language: str = Field(max_length=32)
    timezone: str = Field(max_length=16)
    currency: str = Field(max_length=16)


@router.post()
async def route(schema: CreateAccountSchema):
    result = await AccountService().create(
        username=schema.username,
        password=schema.password,
        firstname=schema.firstname,
        lastname=schema.lastname,
        surname=schema.surname,
        country_id_str=schema.country,
        language_id_str=schema.language,
        timezone_id_str=schema.timezone,
        currency_id_str=schema.currency,
    )
    return Response(**result)
