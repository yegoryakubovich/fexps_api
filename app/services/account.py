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


from math import ceil
from random import sample
from re import compile, search
from string import ascii_letters, digits
from typing import Optional

from app.db.models import Account, Session, Actions, NotificationTypes
from app.repositories import AccountRepository, CountryRepository, LanguageRepository, TimezoneRepository, \
    CurrencyRepository, TextPackRepository, NotificationSettingRepository, WalletRepository, WalletAccountRepository, \
    FileKeyRepository
from app.services.account_role_check_premission import AccountRoleCheckPermissionService
from app.services.base import BaseService
from app.services.file import FileService
from app.services.notification import NotificationService
from app.utils.crypto import create_salt, create_hash_by_string_and_salt
from app.utils.decorators import session_required
from app.utils.exceptions import InvalidPassword, InvalidUsername, ModelAlreadyExist, WrongPassword
from config import settings


class AccountService(BaseService):
    async def create(
            self,
            username: str,
            password: str,
            firstname: str,
            lastname: str,
            country_id_str: str,
            language_id_str: str,
            timezone_id_str: str,
            currency_id_str: str,
    ) -> dict:
        if await AccountRepository().is_exist_by_username(username=username):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Account',
                    'id_type': 'username',
                    'id_value': username,
                }
            )
        await self.is_valid_username(username=username)
        if not await self._is_valid_password(password=password):
            raise InvalidPassword()

        # Generate salt and password hash
        password_salt = await create_salt()
        password_hash = await create_hash_by_string_and_salt(string=password, salt=password_salt)

        # Get other parameters
        country, language, timezone, currency = [
            await repository().get_by_id_str(id_str=id_str)
            for repository, id_str in zip(
                [CountryRepository, LanguageRepository, TimezoneRepository, CurrencyRepository],
                [country_id_str, language_id_str, timezone_id_str, currency_id_str],
            )
        ]

        # Create account
        account = await AccountRepository().create(
            username=username,
            password_salt=password_salt,
            password_hash=password_hash,
            firstname=firstname,
            lastname=lastname,
            country=country,
            language=language,
            timezone=timezone,
            currency=currency,
        )
        # Create action
        await self.create_action(
            model=account,
            action=Actions.CREATE,
            parameters={
                'username': username,
                'firstname': firstname,
                'lastname': lastname,
                'country': country.id_str,
                'language': language.id_str,
                'timezone': timezone.id_str,
                'currency': currency.id_str,
            },
            with_client=True,
        )
        wallet = await WalletRepository().create()
        await WalletAccountRepository().create(account=account, wallet=wallet)
        await NotificationSettingRepository().create(account=account)
        return {
            'id': account.id,
        }

    @session_required(return_model=False, permissions=['accounts'])
    async def get_by_admin(self, id_: int) -> dict:
        account = await AccountRepository().get_by_id(id_=id_)
        return {
            'account': await self.generate_account_dict(account=account),
        }

    @session_required(return_account=True)
    async def get(self, account: Account) -> dict:
        return {
            'account': await self.generate_account_dict(account=account),
        }

    @session_required()
    async def update(
            self,
            session: Session,
            firstname: Optional[str] = None,
            lastname: Optional[str] = None,
            file_key: Optional[str] = None,
    ):
        account: Account = session.account
        updates = {}
        if firstname and firstname != account.firstname:
            updates['firstname'] = firstname
        if lastname and lastname != account.lastname:
            updates['lastname'] = lastname
        if file_key:
            for file_key in await FileKeyRepository().get_list(key=file_key):
                if not file_key.file:
                    continue
                updates['file'] = file_key.file
        if updates:
            await AccountRepository().update(account, **updates)
            await self.create_action(
                model=account,
                action=Actions.UPDATE,
                parameters={
                    'updater': f'session_{session.id}',
                    'account_id': account.id,
                    **updates
                },
                with_client=True,
            )
        return {}

    @session_required(permissions=['accounts'])
    async def change_password_by_admin(
            self,
            session: Session,
            account_id: int,
    ):
        return await self._change_password(
            session=session,
            account_id=account_id,
            by_admin=True,
        )

    @session_required(return_model=False, permissions=['accounts'])
    async def search_by_admin(self, id_, username: str, page: int) -> dict:
        accounts, results = await AccountRepository().search(id_=id_, username=username, page=page)
        accounts = [
            await self.generate_account_dict(account=account)
            for account in accounts
        ]
        return {
            'accounts': accounts,
            'results': results,
            'pages': ceil(results / settings.items_per_page),
            'page': page,
            'items_per_page': settings.items_per_page,
        }

    @session_required()
    async def change_password(
            self,
            session: Session,
            current_password: str,
            new_password: str,
    ):
        return await self._change_password(
            session=session,
            current_password=current_password,
            new_password=new_password,
        )

    async def _change_password(
            self,
            session: Session,
            new_password: str = None,
            current_password: str = None,
            account_id: int = None,
            by_admin: bool = False,
    ):
        generated_password = None
        if by_admin:
            account: Account = await AccountRepository().get_by_id(id_=account_id)
            chars = ascii_letters + digits + '!@#$%^&*'
            while True:
                generated_password = ''.join(sample(chars, 8))
                if await self._is_valid_password(password=generated_password):
                    break
            password_salt = await create_salt()
            password_hash = await create_hash_by_string_and_salt(string=generated_password, salt=password_salt)
        else:
            account: Account = session.account
            await self._is_correct_password(account=account, password=current_password)
            if not await self._is_valid_password(password=new_password):
                raise InvalidPassword()
            password_salt = await create_salt()
            password_hash = await create_hash_by_string_and_salt(string=new_password, salt=password_salt)
        await AccountRepository().update(account, password_salt=password_salt, password_hash=password_hash)
        await NotificationService().create(
            account=account,
            notification_type=NotificationTypes.SYSTEM,
            text_key='notification_global_password_change',
        )
        action_parameters = {
            'account_id': account.id,
            'password_salt': password_salt,
            'password_hash': password_hash,
        }
        if by_admin:
            action_parameters['by_admin'] = True
        await self.create_action(
            model=account,
            action='change_password',
            parameters=action_parameters,
        )
        if generated_password:
            return {
                'new_password': generated_password,
            }
        return {}

    @staticmethod
    async def is_valid_username(username: str):
        register = '^[a-zA-Z][a-zA-Z0-9_]{4,32}$'
        pattern = compile(register)
        if search(pattern, username):
            return True
        raise InvalidUsername()

    async def check_username(
            self,
            username: str,
    ):
        await self.is_valid_username(username=username)
        if await AccountRepository().is_exist_by_username(username=username):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Account',
                    'id_type': 'username',
                    'id_value': username,
                }
            )
        return {}

    async def is_valid_password(
            self,
            password: str,
    ):
        if not await self._is_valid_password(password=password):
            raise InvalidPassword()
        return {}

    @staticmethod
    async def _is_valid_password(password: str):
        if len(password) < 6:
            return False
        return True

    async def check_password(
            self,
            account: Account,
            password: str,
    ):
        await self._is_correct_password(account=account, password=password)

    @staticmethod
    async def _is_correct_password(account: Account, password: str):
        if account.password_hash == await create_hash_by_string_and_salt(
                string=password,
                salt=account.password_salt,
        ):
            return True
        else:
            raise WrongPassword()

    @staticmethod
    async def generate_account_dict(account: Account) -> Optional[dict]:
        if not account:
            return
        text_pack = await TextPackRepository().get_current(language=account.language)
        permissions = await AccountRoleCheckPermissionService().get_permissions(account=account)
        return {
            'id': account.id,
            'username': account.username,
            'firstname': account.firstname,
            'lastname': account.lastname,
            'country': account.country.id_str,
            'language': account.language.id_str,
            'timezone': account.timezone.id_str,
            'currency': account.currency.id_str,
            'file': await FileService().generate_file_dict(file=account.file),
            'permissions': permissions,
            'text_pack_id': text_pack.id,
        }
