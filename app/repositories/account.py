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

from app.db.models import Account
from app.repositories.base import BaseRepository
from app.utils.exceptions import AccountWithUsernameDoeNotExist


class AccountRepository(BaseRepository[Account]):
    model = Account

    async def get_by_username(self, username: str) -> Optional[Account]:
        result = await self.get(username=username)
        if not result:
            raise AccountWithUsernameDoeNotExist(kwargs={'username': username})
        return result

    async def is_exist_by_username(self, username: str) -> bool:
        return self.is_exist(username=username)

    # @staticmethod FIXME
    # async def search(id_, username: str, page: int) -> tuple[list[Account], int]:
    #     if not username:
    #         username = ''
    #     if not id_:
    #         id_ = ''
    #
    #     query = Account.select().where(
    #         (Account.is_deleted == False) &
    #         (Account.username % f'%{username}%') &
    #         (Account.id % f'%{id_}%')
    #     )
    #
    #     accounts = query.limit(
    #         settings.items_per_page
    #     ).offset(settings.items_per_page*(page-1)).order_by(Account.id).execute()
    #     results = query.count()
    #     return accounts, results
