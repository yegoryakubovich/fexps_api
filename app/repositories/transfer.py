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
from typing import List

from sqlalchemy import select

from app.db.models import Transfer
from config import ITEMS_PER_PAGE
from .base import BaseRepository
from ..utils import ApiException


class NotEnoughFundsOnBalance(ApiException):
    pass


class ValueMustBePositive(ApiException):
    pass


class TransferRepository(BaseRepository[Transfer]):
    model = Transfer

    async def search(self, page: int, **filters) -> List[Transfer]:
        async with self._get_session() as session:
            result = await session.execute(
                select(self.model).filter_by(
                    is_deleted=False, **filters
                ).order_by(self.model.id.desc()).limit(ITEMS_PER_PAGE).offset(ITEMS_PER_PAGE * (page - 1))
            )
            return result.scalars().all()
