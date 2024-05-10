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


import datetime

from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.tasks.permanents.telegram.image_poster.bot import send_message
from app.tasks.permanents.telegram.image_poster.image import image_create
from app.tasks.permanents.telegram.logger import TelegramLogger

custom_logger = TelegramLogger(prefix='telegram_image_poster')


async def run():
    image_path = await image_create()
    await send_message(photo=FSInputFile(path=image_path))


async def telegram_image_poster():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run, 'cron', hour=12, minute=00)
    scheduler.start()
