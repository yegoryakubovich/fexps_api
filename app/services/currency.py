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


from app.db.models import Session, Currency, Actions
from app.repositories.currency import CurrencyRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import ModelAlreadyExist, NoRequiredParameters


class CurrencyService(BaseService):
    model = Currency

    @session_required(permissions=['currencies'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            id_str: str,
            decimal: int,
            rate_decimal: int,
            div: int,
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
            decimal=decimal,
            rate_decimal=rate_decimal,
            div=div,
        )
        await self.create_action(
            model=currency,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'id_str': id_str,
                'decimal': decimal,
                'rate_decimal': rate_decimal,
                'div': div,
                'by_admin': True,
            }
        )
        return {'id_str': currency.id_str}

    @staticmethod
    async def get(
            id_str: str,
    ):
        currency = await CurrencyRepository().get_by_id_str(id_str=id_str)
        return {
            'currency': {
                'id': currency.id,
                'id_str': currency.id_str,
                'decimal': currency.decimal,
                'rate_decimal': currency.rate_decimal,
                'div': currency.div,
            }
        }

    @staticmethod
    async def get_list() -> dict:
        currencies = {
            'currencies': [
                {
                    'id': currency.id,
                    'id_str': currency.id_str,
                    'decimal': currency.decimal,
                    'rate_decimal': currency.rate_decimal,
                    'div': currency.div,
                }
                for currency in await CurrencyRepository().get_list()
            ],
        }
        return currencies

    @session_required(permissions=['currencies'], can_root=True)
    async def update_by_admin(
            self,
            session: Session,
            id_str: str,
            decimal: str = None,
            rate_decimal: str = None,
            div: str = None,
    ):
        currency: Currency = await CurrencyRepository().get_by_id_str(id_str=id_str)
        action_parameters = {
            'updater': f'session_{session.id}',
            'id_str': id_str,
            'by_admin': True,
            'decimal': decimal,
            'rate_decimal': rate_decimal,
            'div': div,
        }
        if not decimal and not rate_decimal and not div:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': ['decimal', 'rate_decimal', 'div']
                }
            )
        await CurrencyRepository().update(
            model=currency,
            decimal=decimal,
            rate_decimal=rate_decimal,
            div=div,
        )
        await self.create_action(
            model=currency,
            action=Actions.UPDATE,
            parameters=action_parameters,
        )
        return {}

    @session_required(permissions=['currencies'], can_root=True)
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
