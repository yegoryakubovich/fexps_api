import logging

import aiohttp

from config import settings


class ConnectionManagerAiohttp:
    def __init__(self, token: str, order_id: int):
        self.token = token
        self.order_id = order_id
        self.url = f'{settings.get_chat_url()}?token={self.token}&order_id={self.order_id}'

    async def send(self, text: str = None, files: list = None):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.url) as ws:
                await ws.send_json(
                    data={
                        'text': text,
                        'files': files if files else [],
                    },
                )
