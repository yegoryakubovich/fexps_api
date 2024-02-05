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

from app.permanents.requests.orders_checks import request_new_order_check
from app.permanents.requests.states.input import request_state_input_check
from app.permanents.requests.states.input_reserved import request_state_input_reserved_check
from app.permanents.requests.states.loading import request_state_loading_check
from app.permanents.requests.states.output import request_state_output_check
from app.permanents.requests.states.output_reserved import request_state_output_reserved_check


async def start_app() -> None:
    while True:
        tasks_names = [task.get_name() for task in asyncio.all_tasks()]
        if 'request_new_order_check' not in tasks_names:
            asyncio.create_task(coro=request_new_order_check(), name='request_new_order_check')
        if 'request_state_loading_check' not in tasks_names:
            asyncio.create_task(coro=request_state_loading_check(), name='request_state_loading_check')
        if 'request_state_input_reserved_check' not in tasks_names:
            asyncio.create_task(coro=request_state_input_reserved_check(), name='request_state_input_reserved_check')
        if 'request_state_input_check' not in tasks_names:
            asyncio.create_task(coro=request_state_input_check(), name='request_state_input_check')
        if 'request_state_output_reserved_check' not in tasks_names:
            asyncio.create_task(coro=request_state_output_reserved_check(), name='request_state_output_reserved_check')
        if 'request_state_output_check' not in tasks_names:
            asyncio.create_task(coro=request_state_output_check(), name='request_state_output_check')
        await asyncio.sleep(10 * 60)
