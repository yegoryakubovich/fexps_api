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

from app.db.models import Account
from .base import BaseRepository
from ..utils import ApiException


class AccountWithUsernameDoeNotExist(ApiException):
    pass


class AccountRepository(BaseRepository[Account]):

    async def get_by_username(self, username: str) -> Optional[Account]:
        result = await self.get_all(username=username)
        if not result:
            raise AccountWithUsernameDoeNotExist(f'Account @{username} does not exist')
        return result[0]


account = AccountRepository(Account)
