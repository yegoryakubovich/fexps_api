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


from app.repositories import CurrencyRepository
from app.services.base import BaseService


class CurrencyService(BaseService):
    @staticmethod
    async def get_list() -> dict:
        currencies = {
            'currencies': [
                {
                    'id': currency.id,
                    'id_str': currency.id_str,
                }
                for currency in await CurrencyRepository().get_list()
            ],
        }
        return currencies
