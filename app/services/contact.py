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


from typing import Optional

from app.db.models import Session, Contact, Actions
from app.repositories import TextPackRepository, ContactRepository, TextRepository
from app.services.base import BaseService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required


class ContactService(BaseService):
    model = Contact

    @session_required(permissions=['contacts'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            name: str,
    ) -> dict:
        name_text = await TextRepository().create(
            key=f'contact_{await create_id_str()}',
            value_default=name,
        )
        contact = await ContactRepository().create(name_text=name_text)
        await TextPackRepository().create_all()
        await self.create_action(
            model=contact,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'name_text_id': name_text.id,
            },
        )
        return {
            'id': contact.id,
        }

    async def get(
            self,
            id_: int,
    ):
        contact = await ContactRepository().get_by_id(id_=id_)

        return {
            'contact': await self._generate_contact_dict(contact=contact)
        }

    async def get_list(self) -> dict:
        return {
            'contacts': [
                await self._generate_contact_dict(contact=contact)
                for contact in await ContactRepository().get_list()
            ],
        }

    @session_required(permissions=['contacts'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        contact = await ContactRepository().get(id=id_)
        await ContactRepository().delete(contact)
        await self.create_action(
            model=contact,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )
        return {}

    @staticmethod
    async def _generate_contact_dict(contact: Contact) -> Optional[dict]:
        if not contact:
            return
        return {
            'id': contact.id,
            'name_text': contact.name_text.key,
        }
