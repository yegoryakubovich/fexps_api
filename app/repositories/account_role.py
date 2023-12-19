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


from typing import Optional

import app.repositories as repo
from .base import BaseRepository, ModelDoesNotExist
from app.db.models import AccountRole, Permission, Account


class AccountRoleRepository(BaseRepository[AccountRole]):

    async def get_by_id(self, id_: int) -> Optional[AccountRole]:
        result = await self.get(id_=id_)
        if not result or result.is_deleted:
            raise ModelDoesNotExist(f'{self.model.__name__}.{id_} does not exist')
        return result

    async def delete(self, db_obj: AccountRole) -> Optional[AccountRole]:
        return await self.update(db_obj, is_deleted=True)

    async def get_account_permissions(self, account: Account, only_id_str=False) -> list[str | Permission]:
        result = []
        for account_role in await self.get_all(account_id=account.id, is_deleted=False):
            result += await repo.role_permission.get_permissions_by_role(
                role=account_role.role, only_id_str=only_id_str
            )
        return result


account_role = AccountRoleRepository(AccountRole)
