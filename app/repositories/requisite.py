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


from typing import List

from sqlalchemy import select
from sqlalchemy.sql.operators import or_, and_

from app.db.models import Requisite, RequestTypes, Wallet, RequisiteStates
from app.repositories.base import BaseRepository
from config import settings


class RequisiteRepository(BaseRepository[Requisite]):
    model = Requisite

    async def get_list_input_by_rate(self, **filters) -> List[Requisite]:
        async with self._get_session() as session:
            result = await session.execute(
                select(self.model).order_by(self.model.rate.asc()).filter_by(is_deleted=False, **filters)
            )
            return result.scalars().all()

    async def get_list_output_by_rate(self, **filters) -> List[Requisite]:
        async with self._get_session() as session:
            result = await session.execute(
                select(self.model).order_by(self.model.rate.desc()).filter_by(is_deleted=False, **filters)
            )
            return result.scalars().all()

    async def search(
            self,
            wallets: List[Wallet],
            is_type_input: bool,
            is_type_output: bool,
            is_state_enable: bool,
            is_state_stop: bool,
            is_state_disable: bool,
            page: int,
    ) -> tuple[list[Requisite], int]:
        types = []
        if is_type_input:
            types.append(RequestTypes.INPUT)
        if is_type_output:
            types.append(RequestTypes.OUTPUT)
        if not types:
            return [], 0
        types_where = self.model.type == types.pop()
        for type_ in types:
            types_where = or_(types_where, self.model.type == type_)
        states = []
        if is_state_enable:
            states.append(RequisiteStates.ENABLE)
        if is_state_stop:
            states.append(RequisiteStates.STOP)
        if is_state_disable:
            states.append(RequisiteStates.DISABLE)
        if not states:
            return [], 0
        states_where = self.model.state == states.pop()
        for state in states:
            states_where = or_(states_where, self.model.state == state)
        if not wallets:
            return [], 0
        wallets_where = self.model.wallet_id == wallets.pop().id
        for wallet in wallets:
            wallets_where = or_(wallets_where, self.model.wallet_id == wallet.id)
        custom_where = and_(
            and_(types_where, states_where),
            wallets_where,
        )
        custom_limit = settings.items_per_page
        custom_offset = settings.items_per_page * (page - 1)
        result = await self.get_list(
            custom_where=custom_where,
            custom_limit=custom_limit,
            custom_offset=custom_offset,
        )
        result_count = len(await self.get_list(custom_where=custom_where))
        return result, result_count
