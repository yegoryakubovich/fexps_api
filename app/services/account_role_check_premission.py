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


from app.db.models import Account
from app.repositories import AccountRoleRepository
from app.services.base import BaseService
from app.utils.exceptions import AccountMissingPermission


class AccountRoleCheckPermissionService(BaseService):
    @staticmethod
    async def get_permissions(account: Account):
        permissions = await AccountRoleRepository.get_account_permissions(
            account=account,
            only_id_str=True,
        )
        return permissions

    async def check_permission(self, account: Account, id_str: str):
        if account.id == 0:
            return
        if id_str not in await self.get_permissions(account=account):
            raise AccountMissingPermission(
                kwargs={
                    'id_str': id_str,
                }
            )
