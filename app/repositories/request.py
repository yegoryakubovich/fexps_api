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


from operator import or_
from typing import List

from sqlalchemy.sql.operators import and_

from app.db.models import Request, RequestStates, Wallet
from app.repositories.base import BaseRepository
from config import settings


class RequestRepository(BaseRepository[Request]):
    model = Request

    async def get_list_by_asc(self, **filters) -> List[Request]:
        custom_order = self.model.id.asc()
        return await self.get_list(custom_order=custom_order, **filters)

    async def get_list_not_finished(self, **filters) -> List[Request]:
        custom_where = or_(self.model.state == RequestStates.INPUT, self.model.state == RequestStates.INPUT_RESERVATION)
        return await self.get_list(custom_where=custom_where, **filters)

    async def search(
            self,
            wallets: List[Wallet],
            is_completed: bool,
            is_canceled: bool,
            page: int,
    ) -> tuple[list[Request], int]:
        states = []
        if is_completed:
            states.append(RequestStates.COMPLETED)
        if is_canceled:
            states.append(RequestStates.CANCELED)
        if states:
            states_where = self.model.state == states.pop()
            for state in states:
                states_where = or_(states_where, self.model.state == state)
        else:
            states_where = and_(self.model.state != RequestStates.COMPLETED, self.model.state != RequestStates.CANCELED)
        if wallets:
            wallets_where = self.model.wallet_id == wallets.pop().id
            for wallet in wallets:
                wallets_where = or_(wallets_where, self.model.wallet_id == wallet.id)
        else:
            return [], 0
        custom_where = and_(states_where, wallets_where)
        custom_limit = settings.items_per_page
        custom_offset = settings.items_per_page * (page - 1)
        result = await self.get_list(custom_where=custom_where, custom_limit=custom_limit, custom_offset=custom_offset)
        return result, len(result)
