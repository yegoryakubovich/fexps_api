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

from app.db.models import AccountClientText, Session, Actions
from app.repositories import AccountClientTextRepository, ClientTextRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import AccountClientTextsAlreadyExists


class AccountClientTextService(BaseService):
    model = AccountClientText

    @session_required()
    async def create(
            self,
            session: Session,
            client_text_id: int,
            value: str
    ) -> dict:
        account = session.account
        client_text = await ClientTextRepository().get_by_id(id_=client_text_id)
        if await AccountClientTextRepository().get(account=account, client_text=client_text):
            raise AccountClientTextsAlreadyExists()
        account_client_text = await AccountClientTextRepository().create(
            account=account,
            client_text=client_text,
            value=value,
        )
        await self.create_action(
            model=account_client_text,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'client_text_id': f'{client_text.id}',
                'value': f'{account_client_text.value}',
            },
        )
        return {
            'id': account_client_text.id,
        }

    @session_required()
    async def get(
            self,
            session: Session,
            key: str,
    ) -> dict:
        account = session.account
        client_text = await ClientTextRepository().get(key=key)
        if not client_text:
            return {}
        account_client_text = await AccountClientTextRepository().get(account=account, client_text=client_text)
        return {
            'account_client_text': await self.generate_account_client_text_dict(
                account_client_text=account_client_text,
            ),
        }

    @session_required()
    async def get_list(
            self,
            session: Session,
    ) -> dict:
        account = session.account
        return {
            'accounts_clients_texts': [
                await self.generate_account_client_text_dict(account_client_text=account_client_text)
                for account_client_text in await AccountClientTextRepository().get_list(account=account)
            ],
        }

    @session_required()
    async def update(
            self,
            session: Session,
            id_: int,
            value: str,
    ) -> dict:
        account = session.account
        account_client_text = await AccountClientTextRepository().get_by_account_and_id(account=account, id_=id_)
        await AccountClientTextRepository().update(account_client_text, value=value)
        await self.create_action(
            model=account_client_text,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'value': account_client_text.value,
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
        account_contact = await AccountClientTextRepository().get_by_account_and_id(account=account, id_=id_)
        await AccountClientTextRepository().delete(account_contact)
        await self.create_action(
            model=account_contact,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
            },
        )
        return {}

    @staticmethod
    async def generate_account_client_text_dict(account_client_text: AccountClientText) -> Optional[dict]:
        if not account_client_text:
            return
        return {
            'id': account_client_text.id,
            'client_text_id': account_client_text.client_text.id,
            'client_text_name_key': account_client_text.client_text.name_text.key,
            'value': account_client_text.value,
        }
