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


from app.db.models import Transfer, Wallet, Order, Actions
from app.repositories.transfer import TransferRepository
from app.repositories.wallet import WalletRepository
from app.services.base import BaseService
from app.utils.exceptions.wallet import NotEnoughFundsOnBalance, WalletLimitReached
from app.utils.service_addons.wallet import wallet_get_available_value
from config import settings


async def create_transfer(
        type_: str,
        wallet_from: Wallet,
        wallet_to: Wallet,
        value: float,
        order: Order = None,
        ignore_bal: bool = False,
) -> Transfer:
    balance = wallet_from.value - wallet_from.value_can_minus
    if not ignore_bal and value > balance:
        raise NotEnoughFundsOnBalance()
    available_value = await wallet_get_available_value(wallet=wallet_to)
    if not ignore_bal and value > available_value:
        raise WalletLimitReached(kwargs={'wallet_max_value': settings.wallet_max_value})
    await WalletRepository().update(wallet_from, value=wallet_from.value - value)
    transfer = await TransferRepository().create(
        type=type_,
        wallet_from=wallet_from,
        wallet_to=wallet_to,
        value=value,
        order=order,
    )
    await BaseService().create_action(
        model=transfer,
        action=Actions.CREATE,
        parameters={
            'id': transfer.id,
            'wallet_from_id': wallet_from.id,
            'wallet_to_id': wallet_to.id,
            'value': value
        },
    )
    await WalletRepository().update(wallet_to, value=wallet_to.value + value)
    return transfer
