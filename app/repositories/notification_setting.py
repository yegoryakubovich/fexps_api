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


from app.db.models import NotificationSetting, Account
from app.repositories.base import BaseRepository


class NotificationSettingRepository(BaseRepository[NotificationSetting]):
    model = NotificationSetting

    async def get_by_account(self, account: Account) -> NotificationSetting:
        notification_settings = await self.get(account=account)
        if not notification_settings:
            notification_settings = await self.create(account=account)
        return notification_settings
