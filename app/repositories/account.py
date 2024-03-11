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

from sqlalchemy.sql.operators import and_

from app.db.models import Account
from app.repositories.base import BaseRepository
from app.utils.exceptions import AccountWithUsernameDoeNotExist
from config import settings


class AccountRepository(BaseRepository[Account]):
    model = Account

    async def get_by_username(self, username: str) -> Optional[Account]:
        result = await self.get(username=username)
        if not result:
            raise AccountWithUsernameDoeNotExist(kwargs={'username': username})
        return result

    async def is_exist_by_username(self, username: str) -> bool:
        return await self.is_exist(username=username)

    async def search(self, id_, username: str, page: int) -> tuple[list[Account], int]:
        if not username:
            username = ''
        if not id_:
            id_ = ''
        custom_where = and_(self.model.id.like(f'%{id_}%'), self.model.username.like(f'%{username}%'))
        custom_limit = settings.items_per_page
        custom_offset = settings.items_per_page * (page - 1)
        result = await self.get_list(custom_where=custom_where, custom_limit=custom_limit, custom_offset=custom_offset)
        result_count = len(await self.get_list(custom_where=custom_where))
        return result, result_count
