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
from starlette.responses import HTMLResponse

from app.repositories import MessageRepository
from app.services import MessageService
from app.utils import Router

router = Router(
    prefix='/chat',
)

with open('app/routers/client/messages/html.html') as f:
    html = f.read()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send(self, data):
        for connection in self.active_connections:
            await connection.send_json(data=data)


manager = ConnectionManager()


@router.get("/")
async def get():
    return HTMLResponse(html)


class ChatSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str, order_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            response = await MessageService().create(
                token=token,
                order_id=order_id,
                text=data,
            )
            message = await MessageRepository().get_by_id(id_=response['id'])
            await manager.send(
                data={
                    'account': message.account_id,
                    'order': message.order_id,
                    'text': message.text,
                },
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
