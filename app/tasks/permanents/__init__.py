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

from app import config_logger
from app.tasks.permanents.rates import rate_keep_bybit, rate_our_keep, rate_keep_pair_our
from app.tasks.permanents.requests import request_waiting_check, request_rate_confirmed_check, \
    request_state_loading_check, request_state_input_reserved_check, request_state_input_check, \
    request_state_output_reserved_check, request_state_output_check
from app.tasks.permanents.sync_gd.syncers import sync as go_sync_gd
from app.tasks.permanents.telegram import telegram_image_poster
from app.tasks.permanents.telegram.image_poster import telegram_image_poster
from app.tasks.permanents.telegram.image_updater import telegram_image_updater

TASKS = []
# Request
TASKS += [
    request_waiting_check,
    request_rate_confirmed_check,
    request_state_loading_check,
    request_state_input_reserved_check,
    request_state_input_check,
    request_state_output_reserved_check,
    request_state_output_check,
]
# Rate
TASKS += [
    rate_our_keep,
    rate_keep_pair_our,
    rate_keep_bybit,
]
# Telegram
TASKS += [
    telegram_image_updater,
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
        name='telegram_image_poster',
        func=telegram_image_poster,
        misfire_grace_time=30,
        trigger='cron',
        hour=12,
        minute=0,
    )
    scheduler.add_job(
        name='telegram_image_updater',
        func=telegram_image_updater,
        misfire_grace_time=30,
        trigger='cron',
        minute=0,
    )
    scheduler.start()
    while True:
        tasks_names = [task.get_name() for task in asyncio.all_tasks()]
        [asyncio.create_task(coro=task(), name=task.__name__) for task in TASKS if task.__name__ not in tasks_names]
        await asyncio.sleep(10 * 60)
