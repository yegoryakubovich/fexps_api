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

from app.db.models import Session, Commission, Actions
from app.repositories.commission import CommissionRepository, IntervalAlreadyTaken
from app.services.base import BaseService
from app.utils.decorators import session_required
from config import WALLET_MAX_VALUE


class CommissionService(BaseService):
    model = Commission

    @session_required()
    async def create(
            self,
            session: Session,
            value_from: int,
            value_to: int,
            percent: int,
            value: int,
    ) -> dict:
        await self.check_interval(value_from=value_from, value_to=value_to)
        commission = await CommissionRepository().create(
            value_from=value_from,
            value_to=value_to,
            percent=percent,
            value=value,
        )
        await self.create_action(
            model=commission,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'id': commission.id,
                'value_from': value_from,
                'value_to': value_to,
                'percent': percent,
                'value': value,
            },
        )

        return {'commission_id': commission.id}

    @staticmethod
    async def get_list() -> dict:
        return {
            'commissions': [
                {
                    'id': commission.id,
                    'value_from': commission.value_from,
                    'value_to': commission.value_to,
                    'percent': commission.percent,
                    'value': commission.value,
                }
                for commission in await CommissionRepository().get_list()
            ],
        }

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        commission = await CommissionRepository().get(id=id_)
        await CommissionRepository().delete(commission)
        await self.create_action(
            model=commission,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )

        return {}

    @staticmethod
    async def check_interval(value_from: int, value_to: int):
        new_start = value_from
        new_stop = value_to if value_to != 0 else WALLET_MAX_VALUE
        for commission in await CommissionRepository().get_list():
            commission_start = commission.value_from
            commission_stop = commission.value_to if commission.value_to != 0 else WALLET_MAX_VALUE
            if (new_start <= commission_stop) and (new_stop >= commission_start):
                raise IntervalAlreadyTaken('This interval already taken')
