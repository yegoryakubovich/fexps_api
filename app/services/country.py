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


from app.db.models import Country, Session, Actions
from app.repositories import LanguageRepository, TimezoneRepository, CurrencyRepository, CountryRepository
from app.services.base import BaseService
from app.services.text import TextService
from app.utils.decorators import session_required
from app.utils.exceptions import ModelAlreadyExist, NoRequiredParameters


class CountryService(BaseService):
    model = Country

    @session_required(permissions=['countries'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            id_str: str,
            name: str,
            language: str,
            timezone: str,
            currency: str,
    ):
        if await CountryRepository().is_exist_by_id_str(id_str=id_str):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Country',
                    'id_type': 'id_str',
                    'id_value': id_str,
                }
            )

        language_default = await LanguageRepository().get_by_id_str(id_str=language)
        timezone_default = await TimezoneRepository().get_by_id_str(id_str=timezone)
        currency_default = await CurrencyRepository().get_by_id_str(id_str=currency)

        country = await CountryRepository().create(
            id_str=id_str,
            name=name,
            language_default=language_default,
            timezone_default=timezone_default,
            currency_default=currency_default,
        )

        await self.create_action(
            model=country,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'id_str': id_str,
                'name': name,
                'language': language,
                'timezone': timezone,
                'currency': currency,
                'by_admin': True,
            }
        )

        return {'id_str': country.id_str}

    @session_required(permissions=['countries'])
    async def update_by_admin(
            self,
            session: Session,
            id_str: str,
            name: str = None,
            language: str = None,
            timezone: str = None,
            currency: str = None,
    ):
        country: Country = await CountryRepository().get_by_id_str(id_str=id_str)

        action_parameters = {
            'updater': f'session_{session.id}',
            'id_str': id_str,
            'by_admin': True,
            'name': name,
        }
        if not name and not language and not timezone and not currency:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': ['language', 'timezone', 'currency']
                }
            )
        language_default = None
        if language:
            language_default = await LanguageRepository().get_by_id_str(id_str=language)
            action_parameters.update(language=language)
        timezone_default = None
        if timezone:
            timezone_default = await TimezoneRepository().get_by_id_str(id_str=timezone)
            action_parameters.update(timezone=timezone)
        currency_default = None
        if currency:
            currency_default = await CurrencyRepository().get_by_id_str(id_str=currency)
            action_parameters.update(currency=currency)
        await CountryRepository().update(
            model=country,
            name=name,
            language_default=language_default,
            timezone_default=timezone_default,
            currency_default=currency_default,
        )
        await self.create_action(
            model=country,
            action=Actions.UPDATE,
            parameters=action_parameters,
        )
        return {}

    @session_required(permissions=['countries'])
    async def delete_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        country: Country = await CountryRepository().get_by_id_str(id_str=id_str)

        await TextService().delete_by_admin(session=session, key=f'country_{id_str}')
        await CountryRepository().delete(model=country)

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
