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


from app.db.models import AccountContact, Session
from app.repositories.account_contact import AccountContactRepository
from app.repositories.contact import ContactRepository
from app.services.base import BaseService
from app.utils import ApiException
from app.utils.decorators import session_required


class AccountContactsAlreadyExists(ApiException):
    pass


class AccountContactService(BaseService):
    model = AccountContact

    @session_required()
    async def create(
            self,
            session: Session,
            contact_id: int,
            value: str
    ) -> dict:
        account = session.account
        contact = await ContactRepository().get_by_id(id_=contact_id)
        if await AccountContactRepository().get(account=account, contact=contact):
            raise AccountContactsAlreadyExists('Account Contact has already exists')
        account_contact = await AccountContactRepository().create(account=account, contact=contact, value=value)
        await self.create_action(
            model=contact,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id': f'{account_contact.id}',
                'contact_id': f'{contact.id}',
            },
        )

        return {'account_contact_id': account_contact.id}

    @session_required()
    async def get(
            self,
            session: Session,
            id_: int
    ) -> dict:
        account = session.account
        account_contact = await AccountContactRepository().get_by_account_and_id(account=account, id_=id_)
        contact = await ContactRepository().get_by_id(id_=account_contact.contact.id)

        return {
            'id': account_contact.id,
            'contact_id': contact.id,
            'contact_name_key': contact.name_text.key,
            'value': account_contact.value,
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
    ) -> dict:
        account = session.account
        account_contacts_list = []
        account_contacts = await AccountContactRepository().get_list(account=account)
        for account_contact in account_contacts:
            contact = await ContactRepository().get_by_id(id_=account_contact.contact.id)
            account_contacts_list.append(
                {
                    'id': account_contact.id,
                    'contact_id': contact.id,
                    'contact_name_key': contact.name_text.key,
                    'value': account_contact.value,
                }
            )

        return {'account_contacts': account_contacts_list}

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            value: str,
    ) -> dict:
        account = session.account
        account_contact = await AccountContactRepository().get_by_account_and_id(account=account, id_=id_)
        await AccountContactRepository().update(
            account_contact,
            value=value,
        )

        await self.create_action(
            model=account_contact,
            action='update',
            parameters={
                'updater': f'session_{session.id}',
            },
        )

        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        account_contact = await AccountContactRepository().get_by_account_and_id(account=account, id_=id_)
        await AccountContactRepository().delete(account_contact)
        await self.create_action(
            model=account_contact,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )

        return {}
