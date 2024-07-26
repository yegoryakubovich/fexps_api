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

from app.services.notification import NotificationService
from app.utils import Response, Router

router = Router(
    prefix='/settings',
)


class NotificationUpdateSettingsSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    is_active: Optional[bool] = Field(default=None),
    is_system: Optional[bool] = Field(default=None),
    is_system_email: Optional[bool] = Field(default=None),
    is_system_telegram: Optional[bool] = Field(default=None),
    is_system_push: Optional[bool] = Field(default=None),
    is_request: Optional[bool] = Field(default=None),
    is_request_email: Optional[bool] = Field(default=None),
    is_request_telegram: Optional[bool] = Field(default=None),
    is_request_push: Optional[bool] = Field(default=None),
    is_requisite: Optional[bool] = Field(default=None),
    is_requisite_email: Optional[bool] = Field(default=None),
    is_requisite_telegram: Optional[bool] = Field(default=None),
    is_requisite_push: Optional[bool] = Field(default=None),
    is_chat: Optional[bool] = Field(default=None),
    is_chat_email: Optional[bool] = Field(default=None),
    is_chat_telegram: Optional[bool] = Field(default=None),
    is_chat_push: Optional[bool] = Field(default=None),
    is_transfer: Optional[bool] = Field(default=None),
    is_transfer_email: Optional[bool] = Field(default=None),
    is_transfer_telegram: Optional[bool] = Field(default=None),
    is_transfer_push: Optional[bool] = Field(default=None),


@router.post()
async def route(schema: NotificationUpdateSettingsSchema):
    result = await NotificationService().update_settings(
        token=schema.token,
        is_active=schema.is_active,
        is_system=schema.is_system,
        is_system_email=schema.is_system_email,
        is_system_telegram=schema.is_system_telegram,
        is_system_push=schema.is_system_push,
        is_request=schema.is_request,
        is_request_email=schema.is_request_email,
        is_request_telegram=schema.is_request_telegram,
        is_request_push=schema.is_request_push,
        is_requisite=schema.is_requisite,
        is_requisite_email=schema.is_requisite_email,
        is_requisite_telegram=schema.is_requisite_telegram,
        is_requisite_push=schema.is_requisite_push,
        is_chat=schema.is_chat,
        is_chat_email=schema.is_chat_email,
        is_chat_telegram=schema.is_chat_telegram,
        is_chat_push=schema.is_chat_push,
        is_transfer=schema.is_transfer,
        is_transfer_email=schema.is_transfer_email,
        is_transfer_telegram=schema.is_transfer_telegram,
        is_transfer_push=schema.is_transfer_push,
    )
    return Response(**result)
