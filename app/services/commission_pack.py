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

from app.db.models import Session, CommissionPack, Actions
from app.repositories import TextPackRepository, WalletRepository
from app.repositories.commission_pack import CommissionPackRepository
from app.repositories.commission_pack_value import CommissionPackValueRepository
from app.repositories.text import TextRepository
from app.services.base import BaseService
from app.services.commission_pack_value import CommissionPackValueService
from app.utils.crypto import create_id_str
from app.utils.decorators import session_required


class CommissionPackService(BaseService):
    model = CommissionPack

    @session_required(permissions=['commissions_packs'])
    async def create_by_admin(
            self,
            session: Session,
            name: str,
            is_default: bool,
    ) -> dict:
        name_text = await TextRepository().create(
            key=f'commission_pack_{await create_id_str()}',
            value_default=name,
        )
        await TextPackRepository().create_all()
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
        return {
            'id': commission_pack.id,
        }

    @session_required(permissions=['commissions_packs'])
    async def get_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        commission_pack = await CommissionPackRepository().get_by_id(id_=id_)
        return {
            'commission_pack': await self._generate_commission_pack_dict(commission_pack=commission_pack),
        }

    @session_required(permissions=['commissions_packs'])
    async def get_list_by_admin(
            self,
            session: Session,
    ) -> dict:
        return {
            'commissions_packs': [
                await self._generate_commission_pack_dict(commission_pack=commission_pack)
                for commission_pack in await CommissionPackRepository().get_list()
            ],
        }

    @session_required(permissions=['commissions_packs'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        commission_pack = await CommissionPackRepository().get_by_id(id_=id_)
        for pack_value in await CommissionPackValueRepository().get_list(commission_pack=commission_pack):
            await CommissionPackValueService().delete_by_admin(session=session, id_=pack_value.id)
        new_commission_pack = None
        for pack in await CommissionPackRepository().get_list(is_default=True):
            if pack.id == commission_pack.id:
                continue
            new_commission_pack = pack
            break
        for wallet in await WalletRepository().get_list(commission_pack=commission_pack):
            await WalletRepository().update(wallet, commission_pack=new_commission_pack)
        await TextRepository().delete(commission_pack.name_text)
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

    @staticmethod
    async def _generate_commission_pack_dict(commission_pack: CommissionPack) -> Optional[dict]:
        if not commission_pack:
            return
        return {
            'id': commission_pack.id,
            'name_text': commission_pack.name_text.key,
            'is_default': commission_pack.is_default,
        }
