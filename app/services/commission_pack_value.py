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


from typing import Optional

from app.db.models import CommissionPackValue, Session, Actions, CommissionPack
from app.repositories import CommissionPackRepository, CommissionPackValueRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions import CommissionIntervalAlreadyTaken
from config import settings


class CommissionPackValueService(BaseService):
    model = CommissionPackValue

    @session_required(permissions=['commissions_packs'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            commission_pack_id: int,
            value_from: int,
            value_to: int,
            percent: int,
            value: int,
    ) -> dict:
        commission_pack = await CommissionPackRepository().get_by_id(id_=commission_pack_id)
        await self.commission_pack_check_interval(
            commission_pack=commission_pack,
            value_from=value_from,
            value_to=value_to,
        )
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
        return {
            'id': commission_pack_value.id,
        }

    @session_required(permissions=['commissions_packs'])
    async def get_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        commission_pack_value = await CommissionPackValueRepository().get_by_id(id_=id_)
        return {
            'commission_pack_value': await self.generate_commission_pack_value_dict(
                commission_pack_value=commission_pack_value,
            ),
        }

    @session_required(permissions=['commissions_packs'])
    async def get_list_by_admin(
            self,
            session: Session,
            commission_pack_id: int,
    ) -> dict:
        commission_pack = await CommissionPackRepository().get_by_id(id_=commission_pack_id)
        return {
            'commissions_packs_values': [
                await self.generate_commission_pack_value_dict(commission_pack_value=commission_pack_value)
                for commission_pack_value in await CommissionPackValueRepository().get_list(
                    commission_pack=commission_pack,
                )
            ],
        }

    @session_required(permissions=['commissions_packs'])
    async def delete_by_admin(
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
    async def commission_pack_check_interval(commission_pack: CommissionPack, value_from: int, value_to: int):
        new_start = value_from
        new_stop = value_to if value_to != 0 else settings.wallet_max_value
        for pack_value in await CommissionPackValueRepository().get_list(commission_pack=commission_pack):
            pack_value_start = pack_value.value_from
            pack_value_stop = pack_value.value_to if pack_value.value_to != 0 else settings.wallet_max_value
            if (new_start <= pack_value_stop) and (new_stop >= pack_value_start):
                raise CommissionIntervalAlreadyTaken()

    @staticmethod
    async def generate_commission_pack_value_dict(commission_pack_value: CommissionPackValue) -> Optional[dict]:
        if not commission_pack_value:
            return
        return {
            'id': commission_pack_value.id,
            'commission_pack_id': commission_pack_value.commission_pack_id,
            'value_from': commission_pack_value.value_from,
            'value_to': commission_pack_value.value_to,
            'value': commission_pack_value.value,
            'percent': commission_pack_value.percent,
        }
