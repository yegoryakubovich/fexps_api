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


from app.db.models import Session, CommissionPack, Actions
from app.repositories.commission_pack import CommissionPackRepository
from app.repositories.commission_pack_value import CommissionPackValueRepository
from app.repositories.text import TextRepository
from app.services.base import BaseService
from app.services.commission_pack_value import CommissionPackValueService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required


class CommissionPackService(BaseService):
    model = CommissionPack

    @session_required(permissions=['commissions_packs'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            name: str,
            is_default: bool,
    ) -> dict:
        name_text = await TextRepository().create(
            key=f'method_{await create_id_str()}',
            value_default=name,
        )
        commission_pack = await CommissionPackRepository().create(
            name_text=name_text,
            is_default=is_default,
        )
        await self.create_action(
            model=commission_pack,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'id': commission_pack.id,
                'name_text': name_text.key,
                'is_default': is_default,
            },
        )

        return {'id': commission_pack.id}

    @session_required(permissions=['commissions_packs'], can_root=True)
    async def get_list_by_admin(
            self,
            session: Session,
    ) -> dict:
        commissions_packs = []
        for commission_pack in await CommissionPackRepository().get_list():
            commission_pack_values = []
            for commission_pack_value in await CommissionPackValueRepository().get_list(
                    commission_pack=commission_pack
            ):
                commission_pack_values.append({
                    'value_from': commission_pack_value.value_from, 'value_to': commission_pack_value.value_to,
                    'percent': commission_pack_value.percent, 'value': commission_pack_value.value,
                })
            commissions_packs.append({
                'id': commission_pack.id,
                'name_text': commission_pack.name_text.key,
                'values': commission_pack_values,
                'is_default': commission_pack.is_default,
            })

        return {'commissions_packs': commissions_packs}

    @session_required(permissions=['commissions_packs'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        commission_pack = await CommissionPackRepository().get(id=id_)
        for pack_value in await CommissionPackValueRepository().get_list(commission_pack=commission_pack):
            await CommissionPackValueService().delete(session=session, id_=pack_value.id)
        await CommissionPackRepository().delete(commission_pack)
        await self.create_action(
            model=commission_pack,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )

        return {}
