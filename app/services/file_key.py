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


from time import time

from app.db.models import File, Session, Actions
from app.repositories.file_key import FileKeyRepository
from app.services.base import BaseService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required


class FileKeyService(BaseService):
    model = File

    @session_required()
    async def create(
            self,
            session: Session,
    ) -> dict:
        time_str = str(int(time()))
        key = f'{await create_id_str()}{time_str}'
        file_key = await FileKeyRepository().create(key=key)
        await self.create_action(
            model=file_key,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'key': key,
            },
        )
        return {
            'id': file_key.id,
        }
