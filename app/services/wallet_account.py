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


from app.db.models import WalletAccount, Session, WalletAccountRoles
from app.repositories.account import AccountRepository
from app.repositories.wallet_account import WalletAccountRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class WalletAccountService(BaseService):
    model = WalletAccount

    @session_required()
    async def create(
            self,
            session: Session,
            wallet_id: int,
            account_id: int
    ) -> dict:
        wallet = await WalletAccountRepository().get_by_id(id_=wallet_id)
        account = await AccountRepository().get_by_id(id_=account_id)
        role = WalletAccountRoles.CONFIDANT
        if account.id == session.account.id:
            role = WalletAccountRoles.OWNER
        wallet_account = await WalletAccountRepository().create(wallet=wallet, account=account, role=role)
        await self.create_action(
            model=wallet_account,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'wallet_id': wallet.id,
                'account_id': account.id,
                'role': role,
            },
        )

        return {'wallet_account_id': wallet_account.id}