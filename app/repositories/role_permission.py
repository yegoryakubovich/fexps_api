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
from typing import Optional, List

from app.db.base_repository import BaseRepository
from app.db.models import RolePermission, Role, Permission


class RolePermissionRepository(BaseRepository[RolePermission]):

    async def get_by_id(self, id: int) -> Optional[RolePermission]:
        result = await self.get(id=id)
        if not result:
            return
        if result.is_deleted:
            return
        return result

    async def delete(self, db_obj: RolePermission) -> Optional[RolePermission]:
        return await self.update(db_obj, is_deleted=True)

    async def get_permissions_by_role(self, role: Role, only_id_str=False) -> [List[str], List[Permission]]:
        result = []
        for role_permission in await self.get_all(role=role, is_deleted=False):
            result.append(role_permission.permission.id_str if only_id_str else role_permission.permission)
        return result


role_permission = RolePermissionRepository(RolePermission)
