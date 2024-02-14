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


from app.db.models import CommissionPack
from app.repositories.commission_pack_value import CommissionPackValueRepository
from app.utils.exceptions.commission_pack import CommissionIntervalAlreadyTaken
from config import settings


async def commission_pack_check_interval(commission_pack: CommissionPack, value_from: int, value_to: int):
    new_start = value_from
    new_stop = value_to if value_to != 0 else settings.wallet_max_value
    for pack_value in await CommissionPackValueRepository().get_list(commission_pack=commission_pack):
        pack_value_start = pack_value.value_from
        pack_value_stop = pack_value.value_to if pack_value.value_to != 0 else settings.wallet_max_value
        if (new_start <= pack_value_stop) and (new_stop >= pack_value_start):
            raise CommissionIntervalAlreadyTaken()
