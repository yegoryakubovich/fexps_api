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

from .base import BaseRepository, ModelDoesNotExist
from app.db.models import Permission


class PermissionRepository(BaseRepository[Permission]):

    async def get_by_id(self, id_: int) -> Optional[Permission]:
        result = await self.get(id_=id_)
        if not result or result.is_deleted:
            raise ModelDoesNotExist(f'{self.model.__name__}.{id_} does not exist')
        return result

    async def delete(self, db_obj: Permission) -> Optional[Permission]:
        return await self.update(db_obj, is_deleted=True)

    async def get_by_str_id(self, id_str: str) -> Optional[Permission]:
        async with self.get_session() as session:
            result = await session.execute(select(self.model).where(self.model.id_str == id_str))
            result = result.scalars().first()
        if not result or result.is_deleted:
            raise ModelDoesNotExist(f'{self.model.__name__} "{id_str}" does not exist')
        return result


permission = PermissionRepository(Permission)
