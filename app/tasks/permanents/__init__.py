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
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.tasks.permanents.files.keys.close_check import file_key_close_check
from app.tasks.permanents.rates.keep import rate_keep
from app.tasks.permanents.rates.keep_pair import rate_keep_pair
from app.tasks.permanents.rates.parsers.bybit import rate_parse_bybit
from app.tasks.permanents.requests.rate_fixed_check import request_rate_fixed_check
from app.tasks.permanents.requests.states.confirmation import request_confirmation_check
from app.tasks.permanents.requests.states.input_reserved import request_state_input_reserved_check
from app.tasks.permanents.requests.states.output_reserved import request_state_output_reserved_check
from app.tasks.permanents.requisites.empty_check import empty_check
from app.tasks.permanents.sync_gd import sync as go_sync_gd
from app.tasks.permanents.telegram.send_image import telegram_send_image
from app.tasks.permanents.telegram.send_notification import telegram_send_notification
from app.tasks.permanents.telegram.update_image import telegram_update_image
from app.utils.logger import config_logger

TASKS = []
# File
TASKS += [
    file_key_close_check,
]
# Rate
TASKS += [
    rate_parse_bybit,
]
# Request
TASKS += [
    request_rate_fixed_check,
    request_confirmation_check,
    request_state_input_reserved_check,
    request_state_output_reserved_check,
]
# Requisite
TASKS += [
    empty_check,
]
# Telegram
TASKS += [
    telegram_send_notification,
]


async def start_app() -> None:
    config_logger()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        name='go_sync_gd',
        func=go_sync_gd,
        misfire_grace_time=30,
        trigger='cron',
        minute=0,
        next_run_time=datetime.now(),
    )
    scheduler.add_job(
        name='rate_keep',
        func=rate_keep,
        misfire_grace_time=30,
        trigger='cron',
        minute=00,
    )
    scheduler.add_job(
        name='rate_keep_pair',
        func=rate_keep_pair,
        misfire_grace_time=30,
        trigger='cron',
        minute=59,
    )
    scheduler.add_job(
        name='telegram_image_poster',
        func=telegram_send_image,
        misfire_grace_time=30,
        trigger='cron',
        hour=12,
        minute=1,
    )
    scheduler.add_job(
        name='telegram_image_updater',
        func=telegram_update_image,
        misfire_grace_time=30,
        trigger='cron',
        minute=1,
    )
    scheduler.start()
    while True:
        tasks_names = [task.get_name() for task in asyncio.all_tasks()]
        [asyncio.create_task(coro=task(), name=task.__name__) for task in TASKS if task.__name__ not in tasks_names]
        await asyncio.sleep(10 * 60)
