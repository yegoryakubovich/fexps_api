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

from app.services import NotificationService
from app.utils import Response, Router

router = Router(
    prefix='/settings',
)


class NotificationUpdateSettingsSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    is_request: bool = Field(default=False),
    is_requisite: bool = Field(default=False),
    is_order: bool = Field(default=False),
    is_chat: bool = Field(default=False),
    is_transfer: bool = Field(default=False),
    is_global: bool = Field(default=False),
    is_active: bool = Field(default=False),


@router.post()
async def route(schema: NotificationUpdateSettingsSchema):
    result = await NotificationService().update_settings(
        token=schema.token,
        is_request=schema.is_request,
        is_requisite=schema.is_requisite,
        is_order=schema.is_order,
        is_chat=schema.is_chat,
        is_transfer=schema.is_transfer,
        is_global=schema.is_global,
        is_active=schema.is_active,
    )
    return Response(**result)
