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

from app.services import MessageService
from app.utils import Router
from app.utils.websockets import connections_manager_fastapi


router = Router(
    prefix='/chat',
)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str, order_id: int):
    await connections_manager_fastapi.connect(websocket, order_id=order_id)
    try:
        while True:
            data = await websocket.receive_json()
            response = await MessageService().chat(
                token=token,
                order_id=order_id,
                image_id_str=data.get('image_id_str'),
                text=data['text'],
            )
            await connections_manager_fastapi.send(data=response, order_id=order_id)
    except WebSocketDisconnect:
        connections_manager_fastapi.disconnect(websocket, order_id=order_id)
