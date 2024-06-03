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


from app.db.models import NotificationSetting, Session, Actions
from app.repositories.notification_setting import NotificationSettingRepository
from app.services.base import BaseService
from app.utils.bot.username import get_bot_username, get_chat_username
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required
from app.utils.exceptions import NotificationTelegramAlreadyLinked


class NotificationService(BaseService):
    model = NotificationSetting

    @session_required()
    async def get(
            self,
            session: Session,
    ) -> dict:
        account = session.account
        notification_setting = await NotificationSettingRepository().get(account=account)
        if not notification_setting:
            notification_setting = await NotificationSettingRepository().create(account=account)
        return {
            'notification': await self.generate_notification_dict(notification_setting=notification_setting),
        }

    @session_required()
    async def update_code(
            self,
            session: Session,
    ) -> dict:
        account = session.account
        notification_setting = await NotificationSettingRepository().get(account=account)
        if notification_setting.telegram_id:
            raise NotificationTelegramAlreadyLinked()
        code = await create_id_str()
        await NotificationSettingRepository().update(
            notification_setting,
            code=code,
        )
        await self.create_action(
            model=notification_setting,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'code': code,
            },
        )
        bot_username = await get_bot_username()
        return {
            'code': code,
            'url': f'https://t.me/{bot_username}?start={code}'
        }

    @session_required()
    async def update_settings(
            self,
            session: Session,
            is_request: bool,
            is_requisite: bool,
            is_order: bool,
            is_chat: bool,
            is_transfer: bool,
            is_global: bool,
            is_active: bool,
    ) -> dict:
        account = session.account
        notification_setting = await NotificationSettingRepository().get(account=account)
        await NotificationSettingRepository().update(
            notification_setting,
            is_request=is_request,
            is_requisite=is_requisite,
            is_order=is_order,
            is_chat=is_chat,
            is_transfer=is_transfer,
            is_global=is_global,
            is_active=is_active,
        )
        await self.create_action(
            model=notification_setting,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'is_request': is_request,
                'is_requisite': is_requisite,
                'is_order': is_order,
                'is_chat': is_chat,
                'is_transfer': is_transfer,
                'is_global': is_global,
                'is_active': is_active,
            },
        )
        return {}

    @staticmethod
    async def generate_notification_dict(notification_setting: NotificationSetting):
        return {
            'id': notification_setting.id,
            'telegram_id': notification_setting.telegram_id,
            'username': await get_chat_username(chat_id=notification_setting.telegram_id),
            'is_request': notification_setting.is_request,
            'is_requisite': notification_setting.is_requisite,
            'is_order': notification_setting.is_order,
            'is_chat': notification_setting.is_chat,
            'is_transfer': notification_setting.is_transfer,
            'is_global': notification_setting.is_global,
            'is_active': notification_setting.is_active,
        }
