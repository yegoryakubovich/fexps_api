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


from app.db.models import Role, Session
from app.repositories import RoleRepository, TextRepository
from app.services.base import BaseService
from app.utils import ApiException
from app.utils.decorators import session_required


class RoleAlreadyExist(ApiException):
    pass


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
            raise RoleAlreadyExist(f'Role "{id_str}" already exist')

        name_text = await TextRepository().get_by_key(key=name_text_key)

        role = await RoleRepository.create(
            name_text=name_text,
        )
        await self.create_action(
            model=role,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id_str': id_str,
            },
        )
        return {'role_id': role.id}
