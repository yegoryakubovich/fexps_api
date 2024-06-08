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

from config import settings


class ConnectionManagerAiohttp:
    def __init__(self, token: str, order_id: int):
        self.token = token
        self.order_id = order_id
        self.url = f'{settings.get_chat_url()}?token={self.token}&order_id={self.order_id}'

    async def send(self, role: str, text: str = None, files_key: str = None):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.url) as ws:
                await ws.send_json(
                    data={
                        'role': role,
                        'text': text,
                        'files_key': files_key,
                    },
                )
