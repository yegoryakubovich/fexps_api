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


from fastapi import WebSocket, WebSocketDisconnect
from pydantic import Field, BaseModel

from app.services import MessageService
from app.utils import Router

router = Router(
    prefix='/chat',
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[tuple[int, WebSocket]] = []

    async def connect(self, websocket: WebSocket, order_id: int):
        await websocket.accept()
        self.active_connections.append((order_id, websocket))

    def disconnect(self, websocket: WebSocket, order_id: int):
        self.active_connections.remove((order_id, websocket))

    async def send(self, order_id: int, data):
        for connection in self.active_connections:
            if connection[0] != order_id:
                continue
            await connection[1].send_json(data=data)


manager = ConnectionManager()


class ChatSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str, order_id: int):
    await manager.connect(websocket, order_id=order_id)
    try:
        while True:
            data = await websocket.receive_json()
            response = await MessageService().chat(
                token=token,
                order_id=order_id,
                image_id_str=data.get('image_id_str'),
                text=data['value'],
            )
            await manager.send(data=response, order_id=order_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, order_id=order_id)
