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


from app.db.models import Role, RolePermission, Permission
from .base import BaseRepository


class RolePermissionRepository(Role, BaseRepository):
    model = RolePermission

    @staticmethod
    async def create(
            role: Role,
            permission: Permission,
    ) -> RolePermission:
        return RolePermission.create(
            role=role,
            permission=permission,
        )

    @staticmethod
    async def get_permissions_by_role(role: Role, only_id_str=False) -> list[str]:
        return [
            role_permission.permission.id_str if only_id_str else role_permission.permission
            for role_permission in RolePermission.select().where(
                (RolePermission.role == role) &
                (RolePermission.is_deleted == False)
            )
        ]
