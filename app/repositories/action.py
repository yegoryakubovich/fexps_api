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


from typing import Optional

import app.repositories as repo
from app.db.models import Action, ActionParameter
from .base import BaseRepository


class ActionRepository(BaseRepository[Action]):

    async def create_parameter(self, action: Action, key: str, value: str) -> Optional[ActionParameter]:
        return repo.action_parameter.create(action=action, key=key, value=value)


action = ActionRepository(Action)
