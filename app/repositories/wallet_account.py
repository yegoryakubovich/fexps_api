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


from app.db.models import WalletAccount, Account
from .base import BaseRepository, ModelDoesNotExist


class WalletAccountRepository(BaseRepository[WalletAccount]):
    model = WalletAccount

    async def get_by_account_and_id(self, account: Account, id_: int) -> WalletAccount:
        result = await self.get(account=account, id=id_)
        if not result:
            raise ModelDoesNotExist(f'{self.model.__name__}.{id_} does not exist')
        return result