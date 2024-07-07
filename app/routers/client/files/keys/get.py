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


from fastapi import Depends, WebSocket, WebSocketDisconnect
from pydantic import Field, BaseModel

from app.repositories.file_key import FileKeyRepository
from app.services.file_key import FileKeyService
from app.utils import Response, Router
from app.utils.websockets.file import file_connections_manager_fastapi


router = Router(
    prefix='/get',
)


class FileKeyCreateSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    key: str = Field(min_length=8, max_length=32)


@router.get()
async def route(schema: FileKeyCreateSchema = Depends()):
    result = await FileKeyService().get(
        token=schema.token,
        key=schema.key,
    )
    return Response(**result)


@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await file_connections_manager_fastapi.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            files = FileKeyService().get_ws(key=data['key'])
            await file_connections_manager_fastapi.send(
                data={
                    'key': data['key'],
                    'files': files,
                },
            )
    except WebSocketDisconnect:
        file_connections_manager_fastapi.disconnect(websocket)
