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

from pydantic import BaseModel, Field

from app.services.text import TextService
from app.utils import Response, Router


router = Router(
    prefix='/update',
)


class TextUpdateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    key: str = Field(min_length=1, max_length=128)
    new_key: Optional[str] = Field(default=None, min_length=1, max_length=128)
    value_default: Optional[str] = Field(default=None, min_length=1, max_length=1024)
    create_text_pack: bool = Field(default=True)


@router.post()
async def route(schema: TextUpdateByAdminSchema):
    result = await TextService().update_by_admin(
        token=schema.token,
        key=schema.key,
        value_default=schema.value_default,
        new_key=schema.new_key,
        create_text_pack=schema.create_text_pack,
    )
    return Response(**result)
