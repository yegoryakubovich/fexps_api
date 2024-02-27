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

from app.db.models import Request, RequestStates
from app.repositories.base import BaseRepository


class RequestRepository(BaseRepository[Request]):
    model = Request

    async def get_list_by_asc(self, **filters) -> List[Request]:
        custom_order = self.model.id.asc()
        return await self.get_list(custom_order=custom_order, **filters)

    async def get_list_not_finished(self, **filters) -> List[Request]:
        custom_where = or_(self.model.state == RequestStates.INPUT, self.model.state == RequestStates.INPUT_RESERVATION)
        return await self.get_list(custom_where=custom_where, **filters)
