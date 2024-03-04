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


from sqlalchemy.sql.operators import or_, and_

from app.db.models import Transfer, Wallet
from app.repositories.base import BaseRepository
from config import settings


class TransferRepository(BaseRepository[Transfer]):
    model = Transfer

    async def search_by_wallet(
            self,
            wallet: Wallet,
            is_sender: bool,
            is_receiver: bool,
            page: int = 1,
    ) -> tuple[list[Transfer], int]:
        if is_sender and is_receiver:
            custom_where = or_(self.model.wallet_from == wallet, self.model.wallet_to == wallet)
        elif is_sender and not is_receiver:
            custom_where = self.model.wallet_from == wallet
        elif is_receiver and not is_sender:
            custom_where = self.model.wallet_to == wallet
        else:
            custom_where = and_(self.model.wallet_from == wallet, self.model.wallet_to == wallet)
        custom_limit = settings.items_per_page
        custom_offset = settings.items_per_page * (page - 1)
        result = await self.get_list(custom_where=custom_where, custom_limit=custom_limit, custom_offset=custom_offset)
        return result, len(result)
