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


from fastapi import WebSocket


class ConnectionManagerFastApi:
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


connections_manager_fastapi = ConnectionManagerFastApi()
