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

from sqlalchemy import select

from app.db.base_repository import BaseRepository
from app.db.models import Account


class AccountRepository(BaseRepository[Account]):

    async def get_by_id(self, id: int) -> Optional[Account]:
        result = await self.get(id=id)
        if not result:
            return
        if result.is_deleted:
            return
        return result

    async def delete(self, db_obj: Account) -> Optional[Account]:
        return await self.update(db_obj, is_deleted=True)

    async def get_by_username(self, username: str) -> Account:
        async with self.get_session() as session:
            result = await session.execute(select(self.model).where(self.model.username == username))
            return result.scalars().first()


account = AccountRepository(Account)
