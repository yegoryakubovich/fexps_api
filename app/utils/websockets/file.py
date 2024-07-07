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


import aiohttp
from fastapi import WebSocket

from config import settings


class FileConnectionManagerAiohttp:
    def __init__(self):
        self.url = f'{settings.get_self_url()}/files/keys/get/ws'

    async def send(self, key: str):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.url) as ws:
                await ws.send_json(
                    data={
                        'key': key,
                    },
                )


class FileConnectionManagerFastApi:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send(self, data):
        for connection in self.active_connections:
            await connection.send_json(data=data)


file_connections_manager_fastapi = FileConnectionManagerFastApi()
