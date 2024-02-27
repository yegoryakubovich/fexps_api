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


from app.services.base import BaseService
from app.repositories import RolePermissionRepository, RoleRepository, PermissionRepository
from app.db.models import RolePermission, Session
from app.utils.decorators import session_required


class RolePermissionService(BaseService):
    @session_required(permissions=['roles'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            role_id: int,
            permission_id_str: str,
    ):
        role = await RoleRepository().get_by_id(id_=role_id)
        permission = await PermissionRepository().get_by_id_str(id_str=permission_id_str)

        role_permission = await RolePermissionRepository().create(
            role=role,
            permission=permission
        )

        await self.create_action(
            model=role_permission,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'role_id': role_id,
                'permission': permission_id_str,
                'by_admin': True,
            }
        )

        return {'id': role_permission.id}

    @session_required(permissions=['roles'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        role_permission = await RolePermissionRepository().get_by_id(id_=id_)

        await RolePermissionRepository().delete(model=role_permission)

        await self.create_action(
            model=role_permission,
            action='delete',
            parameters={
                'delete': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @staticmethod
    async def get(
            id_: int
    ):
        role_permission: RolePermission = await RolePermissionRepository().get_by_id(id_=id_)
        return {
            'role_permission': {
                'id': role_permission.id,
                'role_id': role_permission.role.id,
                'permission': role_permission.permission.id_str,
            }
        }

    @staticmethod
    async def get_list(
            role_id: int,
    ):
        role = await RoleRepository().get_by_id(id_=role_id)
        return {
            'role_permissions': [
                {
                    'id': role_permission.id,
                    'permission': role_permission.permission.id_str,
                } for role_permission in await RolePermissionRepository().get_list_by_role(role=role)
            ]
        }
