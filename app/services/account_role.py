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


from app.db.models import AccountRole, Session
from app.repositories import AccountRepository, AccountRoleRepository, RoleRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class AccountRoleService(BaseService):

    @session_required(permissions=['accounts'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            account_id: int,
            role_id: int,
    ):
        account = await AccountRepository().get_by_id(id_=account_id)
        role = await RoleRepository().get_by_id(id_=role_id)
        account_role = await AccountRoleRepository().create(
            account=account,
            role=role,
        )

        await self.create_action(
            model=account_role,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'account_id': account.id,
                'role_id': role.id,
                'by_admin': True,
            }
        )

        return {'id': account_role.id}

    @session_required(permissions=['accounts'])
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        account_role = await AccountRoleRepository().get_by_id(id_=id_)
        await AccountRoleRepository().delete(model=account_role)

        await self.create_action(
            model=account_role,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @session_required(permissions=['accounts'], return_model=False)
    async def get_list_by_admin(self):
        accounts_roles: list[AccountRole] = await AccountRoleRepository().get_list()
        return {
            'accounts_roles': [
                {
                    'id': account_role.id,
                    'account_id': account_role.account.id,
                    'username': account_role.account.username,
                    'role': account_role.role.id,
                } for account_role in accounts_roles
            ]
        }

    @session_required(permissions=['accounts'], return_model=False)
    async def get_by_admin(self, account_id: int):
        account = await AccountRepository().get_by_id(id_=account_id)
        accounts_roles = await AccountRoleRepository().get_by_account(account=account)
        return {
            'accounts_roles': [
                {
                    'id': account_role.id,
                    'role_id': account_role.role.id,
                } for account_role in accounts_roles
            ]
        }
