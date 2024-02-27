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


from app.db.models import Session
from app.repositories import CurrencyRepository
from app.services.base import BaseService
from app.utils.exceptions import ModelAlreadyExist
from app.utils.decorators import session_required


class CurrencyService(BaseService):
    @session_required(permissions=['currencies'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        if await CurrencyRepository().is_exist_by_id_str(id_str=id_str):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Currency',
                    'id_type': 'id_str',
                    'id_value': id_str,
                }
            )

        currency = await CurrencyRepository().create(
            id_str=id_str,
        )

        await self.create_action(
            model=currency,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id_str': id_str,
                'by_admin': True,
            }
        )

        return {'id_str': currency.id_str}

    @session_required(permissions=['currencies'])
    async def delete_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        currency = await CurrencyRepository().get_by_id_str(id_str=id_str)
        await CurrencyRepository().delete(model=currency)

        await self.create_action(
            model=currency,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id_str': id_str,
                'by_admin': True,
            }
        )

        return {}

    @staticmethod
    async def get(
            id_str: str,
    ):
        currency = await CurrencyRepository().get_by_id_str(id_str=id_str)
        return {
            'currency': {
                'id': currency.id,
                'id_str': currency.id_str,
            }
        }

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
