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
from app.repositories import OrderTransferRepository
from app.repositories.transfer import TransferRepository
from app.repositories.wallet import WalletRepository
from app.services.base import BaseService
from app.services.wallet import WalletService


async def create_transfer(
        type_: str,
        wallet_from: Wallet,
        wallet_to: Wallet,
        value: int,
        order: Order = None,
        ignore_bal: bool = False,
) -> Transfer:
    wallet_from = await WalletRepository().get_by_id(id_=wallet_from.id)
    wallet_to = await WalletRepository().get_by_id(id_=wallet_to.id)
    if value < 0:
        value = -value
        wallet_from, wallet_to = wallet_to, wallet_from
    if not ignore_bal:
        await WalletService().check_balance(wallet=wallet_from, value=-value)
        await WalletService().check_balance(wallet=wallet_to, value=value)
    await WalletRepository().update(wallet_from, value=wallet_from.value - value)
    transfer = await TransferRepository().create(
        type=type_,
        wallet_from=wallet_from,
        wallet_to=wallet_to,
        value=value,
    )
    if order:
        await OrderTransferRepository().create(order=order, transfer=transfer)
    await WalletRepository().update(wallet_to, value=wallet_to.value + value)
    await BaseService().create_action(
        model=transfer,
        action=Actions.CREATE,
        parameters={
            'id': transfer.id,
            'type': type_,
            'wallet_from_id': wallet_from.id,
            'wallet_to_id': wallet_to.id,
            'value': value,
            'order': order,
            'ignore_bal': ignore_bal,
        },
    )
    return transfer
