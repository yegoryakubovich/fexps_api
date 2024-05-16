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

from app.db.models import Wallet, CommissionPack
from app.repositories import CommissionPackRepository
from app.repositories.base import BaseRepository


class WalletRepository(BaseRepository[Wallet]):
    model = Wallet

    async def get_system_wallet(self) -> Wallet:
        result = await self.get(is_system=True)
        if not result:
            result = await self.create(name='System', is_system=True)
        return result

    async def get_commission_pack(self, wallet: Wallet) -> Optional[CommissionPack]:
        commission_pack = wallet.commission_pack
        if not commission_pack:
            commission_pack = await CommissionPackRepository().get(is_default=True)
            if not commission_pack:
                return
            await self.update(wallet, commission_pack=commission_pack)
        return commission_pack
