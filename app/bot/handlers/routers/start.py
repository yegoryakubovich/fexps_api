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

from app.repositories import AccountNotificationRepository

start_router = Router()


@start_router.message(Command('start'))
async def start_menu_handler(message: Message, state: FSMContext, command: CommandObject):
    command_code = command.args
    if not command_code:
        await message.answer(text='Not found params')
        return
    account_notification = await AccountNotificationRepository().get(code=command_code)
    if not account_notification:
        await message.answer(text='Not found account')
        return
    await AccountNotificationRepository().update(
        account_notification,
        telegram_id=message.chat.id,
        code=None,
    )
    await message.answer(
        text='\n'.join([
            f'{account_notification.account.username}',
            f'Account verified',
        ])
    )
