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


from app.db.models import WalletAccount, Session, WalletAccountRoles, Actions
from app.repositories.wallet import WalletRepository
from app.repositories.wallet_account import WalletAccountRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from app.utils.exceptions.wallet import WalletPermissionError


class WalletAccountService(BaseService):
    model = WalletAccount

    @session_required()
    async def create(
            self,
            session: Session,
            wallet_id: int,
    ) -> dict:
        account = session.account
        wallet = await WalletRepository().get_by_id(id_=wallet_id)
        role = WalletAccountRoles.CONFIDANT
        if account.id == session.account.id:
            role = WalletAccountRoles.OWNER
        wallet_account = await WalletAccountRepository().create(wallet=wallet, account=account, role=role)
        await self.create_action(
            model=wallet_account,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'wallet_id': wallet.id,
                'account_id': account.id,
                'role': role,
            },
        )
        return {'id': wallet_account.id}

    @session_required()
    async def delete(
            self,
            session: Session,
            id_: int,
    ) -> dict:
        account = session.account
        wallet_account = await WalletAccountRepository().get_by_id(id_=id_)
        if wallet_account.account.id != account.id:
            raise WalletPermissionError()
        await WalletAccountRepository().delete(wallet_account)
        await self.create_action(
            model=wallet_account,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'id': id_,
            },
        )
        return {}
