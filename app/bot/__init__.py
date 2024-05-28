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


import logging

from aiogram.types import BotCommand

from app import config_logger
from app.bot import misc
from app.bot.handlers.routers import main_router
from app.db.init_db import init_db


async def on_startup():
    config_logger()
    logging.info(msg='Bot starting...')
    try:
        await init_db()
        logging.info('Success connect to database')
    except ConnectionRefusedError:
        logging.error('Failed to connect to database')
        exit(1)
    await misc.bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="Start"),
        ],
    )
    misc.dp.include_router(main_router)
    logging.info("Success init")


def create_bot():
    misc.dp.startup.register(on_startup)
    misc.dp.run_polling(misc.bot)
