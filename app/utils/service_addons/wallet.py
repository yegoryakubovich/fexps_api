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


from typing import List

from app.db.models import Wallet, Account
from app.repositories.wallet_account import WalletAccountRepository
from app.utils import ApiException
from app.utils.exceptions.wallet import WalletPermissionError
from config import settings


async def wallet_get_available_value(wallet: Wallet) -> float:  # FIXME
    return settings.wallet_max_value - wallet.value


async def wallet_get_free_value(wallet: Wallet):
    return wallet.value - wallet.value_can_minus


async def wallet_check_permission(
        account: Account,
        wallets: List[Wallet],
        exception: ApiException = WalletPermissionError(),
) -> None:
    permission = False
    for wallet in wallets:
        if await WalletAccountRepository().get(account=account, wallet=wallet):
            permission = True
    if not permission:
        raise exception
