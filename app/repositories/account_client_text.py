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

from app.db.models import AccountClientText, Account
from app.repositories.base import BaseRepository
from app.repositories.client_text import ClientTextRepository
from app.utils.exceptions import ModelDoesNotExist


class AccountClientTextRepository(BaseRepository[AccountClientText]):
    model = AccountClientText

    async def get_by_account_and_id(self, account: Account, id_: int) -> Optional[AccountClientText]:
        result = await self.get(account=account, id=id_)
        if not result:
            raise ModelDoesNotExist(
                kwargs={
                    'model': self.model.__name__,
                    'id_type': 'id',
                    'id': id_,
                },
            )
        return result

    async def get_by_key(self, key: str, **kwargs) -> Optional[AccountClientText]:
        client_text = await ClientTextRepository().get(key=key)
        if not client_text:
            return
        return await self.get(client_text=client_text, **kwargs)
