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


import os
from time import time
from typing import List
from typing import Optional

from fastapi import UploadFile
from starlette.responses import FileResponse

from app.db.models import File, Session, Actions
from app.repositories import FileRepository, OrderRepository, RequestRepository, MessageRepository
from app.repositories.file_key import FileKeyRepository
from app.services.base import BaseService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required
from app.utils.websockets.file import FileConnectionManagerAiohttp
from config import settings


class FileService(BaseService):
    model = File
    model_repositories = {
        'message': MessageRepository,
        'order': OrderRepository,
        'request': RequestRepository,
    }

    @session_required(permissions=['files'])
    async def create_by_admin(
            self,
            session: Session,
            file: UploadFile,
            return_model: bool = False,
    ):
        file = await self._create(
            file=file,
            session=session,
            by_admin=True
        )

        if return_model:
            return file

        return {
            'id_str': file.id_str,
        }

    async def create(
            self,
            key: str,
            files: List[UploadFile],
    ):
        if not await FileKeyRepository().get(file_id=None, key=key):
            return {
                'error': 'key_not_found',
            }
        time_str = str(int(time()))
        for file in files:
            id_str = f'{await create_id_str()}{time_str}'
            extension = file.filename.split('.')[-1]
            with open(f'{settings.path_files}/{id_str}.{extension}', mode='wb') as file_:
                file_.write(await file.read())
            file_db = await FileRepository().create(id_str=id_str, filename=file.filename, extension=extension)
            await FileKeyRepository().create(file=file_db, key=key)
            await self.create_action(
                model=file_db,
                action=Actions.CREATE,
                parameters={
                    'key': key,
                    'id_str': id_str,
                    'filename': file.filename,
                    'extension': extension,
                },
            )
        await FileConnectionManagerAiohttp().send(key=key)
        await FileKeyRepository().delete(await FileKeyRepository().get(file_id=None, key=key))
        return {}

    async def _create(
            self,
            session: Session,
            file: UploadFile,
            by_admin: bool = False,
    ) -> File:
        id_str = await create_id_str()

        extension = file.filename.split('.')[-1]

        action_parameters = {
            'creator': f'session_{session.id}',
            'id_str': id_str,
            'filename': file.filename,
        }

        if by_admin:
            action_parameters.update(by_admin=True)

        with open(f'{settings.path_files}/{id_str}.{extension}', mode='wb') as image:
            file_content = await file.read()
            image.write(file_content)
            image.close()

        image = await FileRepository().create(id_str=id_str, filename=file.filename, extension=extension)
        await self.create_action(
            model=image,
            action=Actions.CREATE,
            parameters=action_parameters
        )
        return image

    @staticmethod
    async def open(id_str: str):
        file = await FileRepository().get_by_id_str(id_str=id_str)
        if file.extension in ['jpg', 'jpeg', 'png', 'pdf']:
            return FileResponse(
                path=f'{settings.path_files}/{file.id_str}.{file.extension}',
            )
        return FileResponse(
            path=f'{settings.path_files}/{file.id_str}.{file.extension}',
            filename=file.filename,
        )

    async def get(self, id_str: str):
        file = await FileRepository().get_by_id_str(id_str=id_str)
        return {
            'file': await self.generate_file_dict(file=file),
        }

    @session_required(permissions=['files'])
    async def delete_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        return await self._delete(
            session=session,
            id_str=id_str,
            by_admin=True,
        )

    @session_required()
    async def delete(
            self,
            session: Session,
            id_str: str,
    ):
        return await self._delete(
            session=session,
            id_str=id_str,
        )

    async def _delete(
            self,
            session: Session,
            id_str: str,
            by_admin: bool = False,
    ):
        file: File = await FileRepository().get_by_id_str(id_str=id_str)
        action_parameters = {
            'deleter': f'session_{session.id}',
            'id_str': id_str,
        }
        if by_admin:
            action_parameters.update(
                {
                    'by_admin': True,
                }
            )
        await FileRepository().delete(model=file)
        os.remove(f'{settings.path_files}/{id_str}.{file.extension}')
        await self.create_action(
            model=file,
            action=Actions.DELETE,
            parameters=action_parameters,
        )
        return {}

    @staticmethod
    async def generate_file_dict(file: File) -> Optional[dict]:
        if not file:
            return
        with open(f'{settings.path_files}/{file.id_str}.{file.extension}', 'rb') as f:
            file_byte = f.read()
        return {
            'id_str': file.id_str,
            'filename': file.filename,
            'extension': file.extension,
            'url': f'{settings.get_file_open_url()}?id_str={file.id_str}',
            'value': file_byte.decode('ISO-8859-1'),
        }
