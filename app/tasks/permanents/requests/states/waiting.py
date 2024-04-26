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


import asyncio
import logging

from app.db.models import Request, Order


def send_log(
        text: str,
        prefix: str = 'request_state_waiting_check',
        func: callable = logging.info,
        request: Request = None,
        order: Order = None,
) -> None:
    log_list = [f'[{prefix}]']
    if order:
        log_list += [
            f'request.{order.request.id} ({order.request.type}:{order.request.state})',
            f'order.{order.id} ({order.type}:{order.state})',
        ]
    elif request:
        log_list += [
            f'request.{request.id} ({request.type}:{request.state})'
        ]
    log_list += [text]
    func(f' '.join(log_list))


async def run():
    await asyncio.sleep(5)


async def request_state_waiting_check():
    send_log(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            send_log(text=f'Exception \n {e}', func=logging.critical)
