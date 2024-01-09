#
# (c) 2023, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
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


from app.db.models import Session, Contact
from app.repositories.contact import ContactRepository
from app.repositories.text import TextRepository
from app.services.base import BaseService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required


class ContactService(BaseService):
    model = Contact

    @session_required()
    async def create(
            self,
            session: Session,
            name: str,
    ) -> dict:
        name_text = await TextRepository().create(
            key=f'contact_{await create_id_str()}',
            value_default=name,
        )
        contact = await ContactRepository().create(name_text=name_text)
        await self.create_action(
            model=contact,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'name_text_id': name_text.id,
            },
        )

        return {'contact_id': contact.id}

    @staticmethod
    async def get(
            id_: int,
    ):
        contact = await ContactRepository().get_by_id(id_=id_)

        return {
            'contact': {
                'id': contact.id,
                'text_key': contact.name_text.key,
            }
        }

    @staticmethod
    async def get_list() -> dict:

        return {
            'contacts': [
                {
                    'id': contact.id,
                    'id_str': contact.name_text.key,
                }
                for contact in await ContactRepository().get_list()
            ],
        }

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        contact = await ContactRepository().get(id=id_)
        await ContactRepository().delete(contact)
        await self.create_action(
            model=contact,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )

        return {}
