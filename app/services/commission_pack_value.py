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


from app.db.models import CommissionPackValue, Session, Actions
from app.repositories.commission_pack import CommissionPackRepository
from app.repositories.commission_pack_value import CommissionPackValueRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.service_addons.commissio_pack_value import commission_pack_check_interval


class CommissionPackValueService(BaseService):
    model = CommissionPackValue

    @session_required(permissions=['commissions_packs'])
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
        await commission_pack_check_interval(
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

        return {'id': commission_pack_value.id}

    @session_required(permissions=['commissions_packs'])
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
