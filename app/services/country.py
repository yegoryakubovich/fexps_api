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


import app.repositories as repo
from app.services.base import BaseService


class CountryService(BaseService):
    @staticmethod
    async def get_list() -> dict:
        # FIXME
        countries = {
            'countries': [
                {
                    'id': country.id,
                    'id_str': country.id_str,
                    'name_text_key': country.name_text.key,
                    'language_default_id_str': (await repo.language.get(country.language_default_id)).id_str,
                    'timezone_default_id_str': (await repo.timezone.get(country.timezone_default_id)).id_str,
                    'currency_default_id_str': (await repo.currency.get(country.currency_default_id)).id_str,

                }
                for country in await repo.country.get_list()
            ],
        }
        return countries
