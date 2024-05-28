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


from app.db.models import Notification, Session, Actions, AccountNotification
from app.repositories.account_notification import AccountNotificationRepository
from app.services.base import BaseService
from app.utils.bot.username import get_bot_username, get_chat_username
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required
from app.utils.exceptions import NotificationTelegramAlreadyLinked


class NotificationService(BaseService):
    model = Notification

    @session_required()
    async def get(
            self,
            session: Session,
    ) -> dict:
        account = session.account
        account_notification = await AccountNotificationRepository().get(account=account)
        return {
            'notification': await self.generate_notification_dict(account_notification=account_notification),
        }

    @session_required()
    async def update_code(
            self,
            session: Session,
    ) -> dict:
        account = session.account
        account_notification = await AccountNotificationRepository().get(account=account)
        if account_notification.telegram_id:
            raise NotificationTelegramAlreadyLinked()
        code = await create_id_str()
        await AccountNotificationRepository().update(
            account_notification,
            code=code,
        )
        await self.create_action(
            model=account_notification,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'code': code,
            },
        )
        bot_username = await get_bot_username()
        return {
            'code': code,
            'link': f'https://t.me/{bot_username}?start={code}'
        }

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            value: str,
    ) -> dict:
        account = session.account
        await AccountNotificationRepository().update()
        await self.create_action(
            model='',
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
            },
        )
        return {}

    @staticmethod
    async def generate_notification_dict(account_notification: AccountNotification):
        return {
            'id': account_notification.id,
            'telegram_id': account_notification.telegram_id,
            'username': await get_chat_username(chat_id=account_notification.telegram_id),
            'is_request_change': account_notification.is_request_change,
            'is_requisite_change': account_notification.is_requisite_change,
            'is_order_change': account_notification.is_order_change,
            'is_chat_change': account_notification.is_chat_change,
            'is_active': account_notification.is_active,
        }
