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
import datetime
from time import time
from typing import Optional

from app.db.models import File, Session, Actions, FileKey
from app.repositories import FileKeyRepository
from app.services import ActionService
from app.services.base import BaseService
from app.services.file import FileService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required
from app.utils.websockets.file import file_connections_manager_fastapi
from config import settings


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
            'key': file_key.key,
            'url': f'{settings.get_self_url()}/files/upload?key={file_key.key}',
        }

    @session_required()
    async def get(
            self,
            session: Session,
            key: str,
    ) -> dict:
        if await FileKeyRepository().get(file_id=None, key=key):
            return {
                'files_keys': [],
            }
        return {
            'files_keys': [
                await self.generate_file_key_dict(file_key=file_key)
                for file_key in await FileKeyRepository().get_list(key=key)
            ],
        }

    @session_required(permissions=['files'], can_root=True)
    async def close_by_task(self, session: Session):
        time_now = datetime.datetime.now(datetime.timezone.utc)
        for file_key in await FileKeyRepository().get_list():
            file_key_action = await ActionService().get_action(file_key, action=Actions.CREATE)
            if not file_key_action:
                continue
            file_key_action_delta = time_now.replace(tzinfo=None) - file_key_action.datetime.replace(tzinfo=None)
            if file_key_action_delta < datetime.timedelta(minutes=settings.file_key_close_minutes):
                continue
            await FileKeyRepository().delete(file_key)
        return {}

    async def get_ws(self, key: str):
        files = [
            await self.generate_file_key_dict(file_key=file_key)
            for file_key in await FileKeyRepository().get_list(key=key)
        ]
        [files.remove({}) for i in range(files.count({}))]
        return files

    @staticmethod
    async def generate_file_key_dict(file_key: FileKey) -> Optional[dict]:
        if not file_key.file:
            return {}
        return {
            'key': file_key.key,
            'file_key_id': file_key.id,
            **await FileService().generate_file_dict(file=file_key.file),
        }

    async def send_file(self, key: str):
        await file_connections_manager_fastapi.send(
            data={
                'key': key,
                'files': await self.get_ws(key=key),
            },
        )
