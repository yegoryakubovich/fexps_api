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


from app.db.models import Role, Session
from app.repositories import RolePermissionRepository, RoleRepository
from app.services.text import TextService
from app.services.base import BaseService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required


class RoleService(BaseService):
    @session_required(permissions=['roles'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            name: str,
    ):
        name_text = await TextService().create_by_admin(
            session=session,
            key=f'role_{await create_id_str()}',
            value_default=name,
            return_model=True,
        )

        role = await RoleRepository().create(
            name_text=name_text,
        )

        await self.create_action(
            model=role,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'name_text': name_text.key,
                'by_admin': True,
            }
        )

        return {'id': role.id}

    @session_required(permissions=['roles'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        role = await RoleRepository().get_by_id(id_=id_)

        await TextService().delete_by_admin(
            session=session,
            key=role.name_text.key,
        )

        await RoleRepository().delete(model=role)

        await self.create_action(
            model=role,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @staticmethod
    async def get(
            id_: int,
    ):
        role: Role = await RoleRepository().get_by_id(id_=id_)
        return {
            'role': {
                'id': role.id,
                'name_text': role.name_text.key,
                'permissions': await RolePermissionRepository().get_permissions_by_role(role=role, only_id_str=True)
            }
        }

    @staticmethod
    async def get_list():
        return {
            'roles': [
                {
                    'id': role.id,
                    'name_text': role.name_text.key,
                    'permissions': await RolePermissionRepository().get_permissions_by_role(role=role, only_id_str=True)
                } for role in await RoleRepository().get_list()
            ]
        }
