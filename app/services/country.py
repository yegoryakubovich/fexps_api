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


from app.db.models import Country, Session
from app.repositories import CountryRepository, CurrencyRepository, LanguageRepository, TimezoneRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import ModelAlreadyExist, NoRequiredParameters


class CountryService(BaseService):
    @session_required(permissions=['countries'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            id_str: str,
            name: str,
            language_default_id_str: str,
            timezone_default_id_str: str,
            currency_default_id_str: str,
    ):
        if await CountryRepository().is_exist_by_id_str(id_str=id_str):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Country',
                    'id_type': 'id_str',
                    'id_value': id_str,
                }
            )
        language_default = await LanguageRepository().get_by_id_str(id_str=language_default_id_str)
        timezone_default = await TimezoneRepository().get_by_id_str(id_str=timezone_default_id_str)
        currency_default = await CurrencyRepository().get_by_id_str(id_str=currency_default_id_str)
        country = await CountryRepository().create(
            id_str=id_str,
            name=name,
            language_default=language_default,
            timezone_default=timezone_default,
            currency_default=currency_default,
        )
        await self.create_action(
            model=country,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id_str': id_str,
                'name': name,
                'language_default': language_default_id_str,
                'timezone_default': timezone_default_id_str,
                'currency_default': currency_default_id_str,
                'by_admin': True,
            }
        )
        return {'id_str': country.id_str}

    @session_required(permissions=['countries'], can_root=True)
    async def update_by_admin(
            self,
            session: Session,
            id_str: str,
            language_default_id_str: str = None,
            timezone_default_id_str: str = None,
            currency_default_id_str: str = None,
    ):
        country: Country = await CountryRepository().get_by_id_str(id_str=id_str)
        action_parameters = {
            'updater': f'session_{session.id}',
            'id_str': id_str,
            'by_admin': True,
        }
        if not language_default_id_str and not timezone_default_id_str and not currency_default_id_str:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': ['language', 'timezone', 'currency']
                }
            )
        language_default = None
        if language_default_id_str:
            language_default = await LanguageRepository().get_by_id_str(id_str=language_default_id_str)
            action_parameters.update(language=language_default_id_str)
        timezone_default = None
        if timezone_default_id_str:
            timezone_default = await TimezoneRepository().get_by_id_str(id_str=timezone_default_id_str)
            action_parameters.update(timezone=timezone_default_id_str)
        currency_default = None
        if currency_default_id_str:
            currency_default = await CurrencyRepository().get_by_id_str(id_str=currency_default_id_str)
            action_parameters.update(currency=currency_default_id_str)
        await CountryRepository().update(
            model=country,
            language_default=language_default,
            timezone_default=timezone_default,
            currency_default=currency_default,
        )
        await self.create_action(
            model=country,
            action='update',
            parameters=action_parameters,
        )
        return {}

    @session_required(permissions=['countries'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        country: Country = await CountryRepository().get_by_id_str(id_str=id_str)
        await CountryRepository().delete(model=country)
        await self.create_action(
            model=country,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id_str': id_str,
                'by_admin': True,
            }
        )
        return {}

    async def get(
            self,
            id_str: str,
    ):
        country: Country = await CountryRepository().get_by_id_str(id_str=id_str)
        return {
            'country': await self._generate_country_dict(country=country)
        }

    async def get_list(self) -> dict:
        return {
            'countries': [
                await self._generate_country_dict(country=country)
                for country in await CountryRepository().get_list()
            ]
        }

    @staticmethod
    async def _generate_country_dict(country: Country):
        return {
            'id': country.id,
            'id_str': country.id_str,
            'name': country.name,
            'language': country.language_default.id_str,
            'timezone': country.timezone_default.id_str,
            'currency': country.currency_default.id_str,
        }
