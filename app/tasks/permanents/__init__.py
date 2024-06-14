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
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app import config_logger, init_db
from app.tasks.permanents.files import file_key_close_check
from app.tasks.permanents.rates import rate_keep_bybit_parse, rate_keep, rate_keep_pair
from app.tasks.permanents.requests import request_confirmation_check, request_rate_fixed_check, \
    request_state_input_reserved_check, request_state_input_check, request_state_output_reserved_check, \
    request_state_output_check
from app.tasks.permanents.sync_gd.syncers import sync as go_sync_gd
from app.tasks.permanents.telegram import telegram_image_poster
from app.tasks.permanents.telegram.image_poster import telegram_image_poster
from app.tasks.permanents.telegram.image_updater import telegram_image_updater

TASKS = []
# Request
TASKS += [
    request_rate_fixed_check,
    request_confirmation_check,
    request_state_input_reserved_check,
    request_state_input_check,
    request_state_output_reserved_check,
    request_state_output_check,
]
# File
TASKS += [
    file_key_close_check,
]
# Rate
TASKS += [
    rate_keep_bybit_parse,
]


async def start_app() -> None:
    config_logger()
    try:
        await init_db()
        logging.info('Success connect to database')
    except ConnectionRefusedError:
        logging.error('Failed to connect to database')
        exit(1)
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
        func=telegram_image_poster,
        misfire_grace_time=30,
        trigger='cron',
        hour=12,
        minute=1,
    )
    scheduler.add_job(
        name='telegram_image_updater',
        func=telegram_image_updater,
        misfire_grace_time=30,
        trigger='cron',
        minute=1,
    )
    scheduler.start()
    while True:
        tasks_names = [task.get_name() for task in asyncio.all_tasks()]
        [asyncio.create_task(coro=task(), name=task.__name__) for task in TASKS if task.__name__ not in tasks_names]
        await asyncio.sleep(10 * 60)
