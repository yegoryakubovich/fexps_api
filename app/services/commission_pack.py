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

    @session_required()
    async def create(
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

        return {'commission_pack_id': commission_pack.id}

    @session_required()
    async def create_interval(
            self,
            session: Session,
            id_: int,
            value_from: int,
            value_to: int,
            percent: int,
            value: int,
    ) -> dict:
        result = await CommissionPackValueService().create(
            session=session,
            commission_pack_id=id_,
            value_from=value_from,
            value_to=value_to,
            percent=percent,
            value=value,
        )

        return result

    @staticmethod
    async def get_list() -> dict:
        return {
            'commissions_packs': [
                {
                    'id': commission_pack.id,
                    'name_text': commission_pack.name_text.key,
                    'default_pack': commission_pack.is_default,
                }
                for commission_pack in await CommissionPackRepository().get_list()
            ],
        }

    @session_required()
    async def delete(
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
