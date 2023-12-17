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


from app.db.models import Account
from app.repositories import AccountRepository, CountryRepository, LanguageRepository, TimezoneRepository, \
    CurrencyRepository, TextPackRepository
from app.services import AccountRoleService
from app.services.base import BaseService
from app.utils import ApiException
from app.utils.crypto import create_salt, create_hash_by_string_and_salt
from app.utils.decorators import session_required


class WrongPassword(ApiException):
    pass


class AccountUsernameExist(ApiException):
    pass


class AccountMissingRole(ApiException):
    pass


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
            surname: str = None,
    ) -> dict:
        if await AccountRepository.is_exist(username=username):
            raise AccountUsernameExist(f'Account with username "{username}" already exist')

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
        account = await AccountRepository.create(
            username=username,
            password_salt=password_salt,
            password_hash=password_hash,
            firstname=firstname,
            lastname=lastname,
            surname=surname,
            country=country,
            language=language,
            timezone=timezone,
            currency=currency,
        )
        # Create action
        await self.create_action(
            model=account,
            action='create',
            parameters={
                'username': username,
                'firstname': firstname,
                'lastname': lastname,
                'surname': surname,
                'country': country.id_str,
                'language': language.id_str,
                'timezone': timezone.id_str,
                'currency': currency.id_str,
            },
            with_client=True,
        )
        return {'account_id': account.id}

    async def check_password(
            self,
            account: Account,
            password: str,
    ):
        await self._is_correct_password(account=account, password=password)
        return True

    @staticmethod
    async def check_username(
            username: str,
    ):
        if await AccountRepository.is_exist(username=username):
            raise AccountUsernameExist(f'Account with username "{username}" already exist')
        return {}

    @session_required(return_account=True)
    async def get(self, account: Account) -> dict:
        text_pack = await TextPackRepository.get_current(language=account.language)
        permissions = await AccountRoleService.get_permissions(account=account)

        return {
            'username': account.username,
            'firstname': account.firstname,
            'lastname': account.lastname,
            'surname': account.surname,
            'country': account.country.id_str,
            'language': account.language.id_str,
            'timezone': account.timezone.id_str,
            'currency': account.currency.id_str,
            'permissions': permissions,
            'text_pack_id': text_pack.id,
        }

    @staticmethod
    async def _is_correct_password(account: Account, password: str):
        if account.password_hash == await create_hash_by_string_and_salt(
                string=password,
                salt=account.password_salt,
        ):
            return True
        else:
            raise WrongPassword('Wrong password')
