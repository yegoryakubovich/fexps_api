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
from app.db.models import Currency


class CurrencyRepository(BaseRepository[Currency]):

    async def get_by_id(self, id: int) -> Optional[Currency]:
        result = await self.get(id=id)
        if not result:
            return
        if result.is_deleted:
            return
        return result

    async def delete(self, db_obj: Currency) -> Optional[Currency]:
        return await self.update(db_obj, is_deleted=True)

    async def get_by_str_id(self, id_str: str) -> Optional[Currency]:
        async with self.get_session() as session:
            result = await session.execute(select(self.model).where(self.model.id_str == id_str))
            result = result.scalars().first()
        if not result:
            return
        if result.is_deleted:
            return
        return result


currency = CurrencyRepository(Currency)
