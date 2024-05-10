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

from app import config_logger
from app.tasks.permanents.rates import rate_keep, rate_keep_pair
from app.tasks.permanents.requests import request_waiting_check, request_rate_confirmed_check, \
    request_state_loading_check, request_state_input_reserved_check, request_state_input_check, \
    request_state_output_reserved_check, request_state_output_check
from app.tasks.permanents.requisites import requisite_balance_out_check
from app.tasks.permanents.sync_gd import sync_gd
from app.tasks.permanents.telegram import telegram_image_poster

TASKS = []
# Request
TASKS += [
    # request_waiting_check,
    # request_rate_confirmed_check,
    # request_state_loading_check,
    # request_state_input_reserved_check,
    # request_state_input_check,
    # request_state_output_reserved_check,
    # request_state_output_check,
]
# Requisite
TASKS += [
    # requisite_balance_out_check,
]
# Rate
TASKS += [
    # rate_keep,
    # rate_keep_pair,
]
# Google Drive
TASKS += [
    sync_gd,
]
# Telegram
TASKS += [
    telegram_image_poster,
]


async def start_app() -> None:
    config_logger()
    while True:
        tasks_names = [task.get_name() for task in asyncio.all_tasks()]
        [asyncio.create_task(coro=task(), name=task.__name__) for task in TASKS if task.__name__ not in tasks_names]
        await asyncio.sleep(10 * 60)
