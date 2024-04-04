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


from app.db.models import Message, Session, Actions
from app.repositories import MessageRepository, OrderRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class MessageService(BaseService):
    model = Message

    @session_required()
    async def create(
            self,
            session: Session,
            order_id: int,
            text: str,
    ):
        account = session.account
        order = await OrderRepository().get_by_id(id_=order_id)
        message = await MessageRepository().create(
            account=account,
            order=order,
            text=text,
        )
        await self.create_action(
            model=message,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'order_id': order_id,
                'text': text,
            }
        )
        return {'id': message.id}
