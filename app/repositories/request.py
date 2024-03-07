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

from app.db.models import Request, RequestStates, Wallet, RequestTypes
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
            is_input: bool,
            is_output: bool,
            is_all: bool,
            is_finish: bool,
            page: int,
    ) -> tuple[list[Request], int]:
        types = []
        if is_input:
            types.append(RequestTypes.INPUT)
        if is_output:
            types.append(RequestTypes.OUTPUT)
        if is_all:
            types.append(RequestTypes.ALL)
        if types:
            types_where = self.model.type == types.pop()
            for type_ in types:
                types_where = or_(types_where, self.model.type == type_)
        else:
            return [], 0
        if wallets:
            wallets_where = self.model.wallet_id == wallets.pop().id
            for wallet in wallets:
                wallets_where = or_(wallets_where, self.model.wallet_id == wallet.id)
        else:
            return [], 0
        custom_where = and_(types_where, wallets_where)
        custom_limit = settings.items_per_page
        custom_offset = settings.items_per_page * (page - 1)
        result = await self.get_list(custom_where=custom_where, custom_limit=custom_limit, custom_offset=custom_offset)
        return result, len(result)
