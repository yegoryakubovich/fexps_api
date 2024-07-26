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


from app.db.models import Session, Actions
from app.repositories import AccountRepository, SessionRepository
from app.services.account import AccountService
from app.services.base import BaseService
from app.services.notification import NotificationService
from app.utils.crypto import create_salt, create_hash_by_string_and_salt


class SessionService(BaseService):
    model = Session

    async def create(self, username: str, password: str) -> dict:
        account = await AccountRepository().get_by_username(username=username)
        await AccountService().check_password(account=account, password=password)
        # Create token hash
        token = await create_salt()
        token_salt = await create_salt()
        token_hash = await create_hash_by_string_and_salt(string=token, salt=token_salt)
        # Create session
        session = await SessionRepository().create(account=account, token_hash=token_hash, token_salt=token_salt)
        await NotificationService().create_notification_system_session_new_auth(account=account)
        await self.create_action(
            model=session,
            action=Actions.CREATE,
            with_client=True,
        )
        token = f'{session.id:08}:{token}'
        return {
            'session': {
                'id': session.id,
                'token': token,
            },
        }
