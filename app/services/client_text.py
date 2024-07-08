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


from app.db.models import ClientText, Session, Actions
from app.repositories import ClientTextRepository
from app.services.base import BaseService
from app.services.text import TextService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required


class ClientTextService(BaseService):
    model = ClientText

    @session_required(permissions=['clients_texts'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            key: str,
            name: str,
    ):
        name_text = await TextService().create_by_admin(
            session=session,
            key=f'client_text_{await create_id_str()}',
            value_default=name,
            return_model=True,
        )
        client_text = await ClientTextRepository().create(key=key, name_text=name_text)
        await self.create_action(
            model=client_text,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'key': key,
                'name': name,
                'name_text': name_text.key,
            },
        )
        return {
            'id': client_text.id,
        }

    async def get(self, id_: int):
        client_text = await ClientTextRepository().get_by_id(id_=id_)
        return {
            'client_text': await self.generate_client_text_dict(client_text=client_text)
        }

    async def get_list(self):
        return {
            'clients_texts': [
                await self.generate_client_text_dict(client_text=client_text)
                for client_text in await ClientTextRepository().get_list()
            ],
        }

    @session_required(permissions=['clients_texts'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        client_text = await ClientTextRepository().get_by_id(id_=id_)
        await TextService().delete_by_admin(
            session=session,
            key=client_text.name_text.key,
        )
        await ClientTextRepository().delete(client_text)
        await self.create_action(
            model=client_text,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            },
        )
        return {}

    @staticmethod
    async def generate_client_text_dict(client_text: ClientText) -> dict:
        return {
            'id': client_text.id,
            'key': client_text.key,
            'name_text': client_text.name_text.key,
        }
