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

from app.db.models import Requisite
from app.repositories import RequisiteRepository


async def calculate_requisite_process_change_list(
        requisites: [list[Requisite], list[int]],
        in_process: bool,
        process: bool,
) -> Optional[tuple[int, int]]:
    if not process:
        return
    for requisite in requisites:
        if isinstance(requisite, int):
            requisite = await RequisiteRepository().get_by_id(id_=requisite)
        await RequisiteRepository().update(requisite, in_process=in_process)


async def calculate_requisite_process_change(
        requisite: [Requisite, int],
        in_process: bool,
        process: bool,
) -> Optional[tuple[int, int]]:
    if not process:
        return
    if isinstance(requisite, int):
        requisite = await RequisiteRepository().get_by_id(id_=requisite)
    await RequisiteRepository().update(requisite, in_process=in_process)
