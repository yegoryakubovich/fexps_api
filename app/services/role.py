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


from app.db.models import Role, Session, Actions
from app.repositories.role import RoleRepository
from app.repositories.text import TextRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions.role import RoleAlreadyExist


class RoleService(BaseService):
    model = Role

    @session_required(permissions=['create_roles'])
    async def create(
            self,
            session: Session,
            id_str: str,
            name_text_key: str,
    ) -> dict:
        if await RoleRepository().is_exist(id_str=id_str):
            raise RoleAlreadyExist(kwargs={'id_str': id_str})

        name_text = await TextRepository().get_by_key(key=name_text_key)
        role = await RoleRepository().create(name_text=name_text)
        await self.create_action(
            model=role,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'id_str': id_str,
            },
        )

        return {'id': role.id}
