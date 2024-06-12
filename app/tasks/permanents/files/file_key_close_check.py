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
import datetime

from app.db.models import Actions
from app.repositories.file_key import FileKeyRepository
from app.services import ActionService
from app.tasks.permanents.files.logger import FileLogger
from config import settings

custom_logger = FileLogger(prefix='file_key_close_check')


async def run():
    time_now = datetime.datetime.now(datetime.UTC)
    for file_key in await FileKeyRepository().get_list():
        await asyncio.sleep(0.5)
        file_key_action = await ActionService().get_action(file_key, action=Actions.CREATE)
        if not file_key_action:
            continue
        file_key_action_delta = time_now.replace(tzinfo=None) - file_key_action.datetime.replace(tzinfo=None)
        if file_key_action_delta < datetime.timedelta(minutes=settings.file_key_close_minutes):
            continue
        await FileKeyRepository().delete(file_key)
    await asyncio.sleep(1)


async def file_key_close_check():
    custom_logger.info(text=f'started...')
    while True:
        try:
            await run()
        except ValueError as e:
            custom_logger.critical(text=f'Exception \n {e}')
