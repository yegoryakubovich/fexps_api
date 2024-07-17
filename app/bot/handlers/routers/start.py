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


from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.tasks.permanents.utils.fexps_api_client import fexps_api_client
from app.utils import ApiException

start_router = Router()


@start_router.message(Command('start'))
async def start_menu_handler(message: Message, state: FSMContext, command: CommandObject):
    command_code = command.args
    if not command_code:
        await message.answer(text='Not found params')
        return
    try:
        await fexps_api_client.admin.notifications.update(code=command_code, telegram_id=message.chat.id)
        await message.answer(text='Account verified')
    except ApiException as exception:
        await message.answer(text=exception.message)
