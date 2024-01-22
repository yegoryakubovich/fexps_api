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


from app.db.models import AccountRole, Permission, Account
from app.repositories.role_permission import RolePermissionRepository
from .base import BaseRepository


class AccountRoleRepository(BaseRepository[AccountRole]):
    model = AccountRole

    async def get_account_permissions(self, account: Account, only_id_str=False) -> list[str | Permission]:
        result = []
        for account_role in await self.get_list(account_id=account.id):
            result += await RolePermissionRepository().get_permissions_by_role(
                role=account_role.role, only_id_str=only_id_str
            )
        return result
