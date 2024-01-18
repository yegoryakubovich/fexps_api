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
from sqlalchemy.sql.operators import and_

from app.db.models import CommissionPack
from .base import BaseRepository
from ..utils import ApiException


class IntervalAlreadyTaken(ApiException):
    pass


class IntervalValidationError(ApiException):
    pass


class IntervalNotFoundError(ApiException):
    pass


class CommissionPackRepository(BaseRepository[CommissionPack]):
    model = CommissionPack

    async def get_by_value(self, value: int):
        custom_where = and_(self.model.value_from <= value, value <= self.model.value_to)
        result = await self.get(custom_where=custom_where)
        if not result:
            custom_where = and_(self.model.value_from <= value, self.model.value_to == 0)
            result = await self.get(custom_where=custom_where)
        return result
