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

from app.db.models import CommissionPackValue, CommissionPack, Session, Actions
from app.repositories.commission_pack import CommissionPackRepository
from app.repositories.commission_pack_value import CommissionPackValueRepository
from app.services.base import BaseService
from app.utils import ApiException
from app.utils.decorators import session_required
from config import WALLET_MAX_VALUE


class IntervalAlreadyTaken(ApiException):
    pass


class IntervalValidationError(ApiException):
    pass


class IntervalNotFoundError(ApiException):
    pass


class CommissionPackValueService(BaseService):
    model = CommissionPackValue

    @session_required()
    async def create(
            self,
            session: Session,
            commission_pack_id: int,
            value_from: int,
            value_to: int,
            percent: int,
            value: int,
    ) -> dict:
        commission_pack = await CommissionPackRepository().get_by_id(id_=commission_pack_id)
        await self.check_interval(commission_pack=commission_pack, value_from=value_from, value_to=value_to)
        commission_pack_value = await CommissionPackValueRepository().create(
            commission_pack=commission_pack,
            value_from=value_from,
            value_to=value_to,
            percent=percent,
            value=value,
        )
        await self.create_action(
            model=commission_pack_value,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'id': commission_pack_value.id,
                'commission_pack_id': commission_pack_id,
                'value_from': value_from,
                'value_to': value_to,
                'percent': percent,
                'value': value,
            },
        )

        return {'commission_pack_value_id': commission_pack_value.id}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        commission_pack_value = await CommissionPackValueRepository().get(id=id_)
        await CommissionPackValueRepository().delete(commission_pack_value)
        await self.create_action(
            model=commission_pack_value,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )

        return {}

    @staticmethod
    async def check_interval(commission_pack: CommissionPack, value_from: int, value_to: int):
        new_start = value_from
        new_stop = value_to if value_to != 0 else WALLET_MAX_VALUE
        for pack_value in await CommissionPackValueRepository().get_list(commission_pack=commission_pack):
            pack_value_start = pack_value.value_from
            pack_value_stop = pack_value.value_to if pack_value.value_to != 0 else WALLET_MAX_VALUE
            if (new_start <= pack_value_stop) and (new_stop >= pack_value_start):
                raise IntervalAlreadyTaken('This interval already taken')
