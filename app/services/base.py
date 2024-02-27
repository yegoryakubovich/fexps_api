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


from json import dumps

from inflection import underscore

from app.db.models.base import BaseModel
from app.services.action import ActionService
from app.utils import client


class BaseService:
    @staticmethod
    async def create_action(
            model: BaseModel,
            action: str,
            with_client: bool = False,
            parameters: dict = None,
    ):
        if not parameters:
            parameters = {}
        if with_client:
            parameters['client_host'] = client.host
            parameters['client_device'] = dumps(client.device.__dict__)
        await ActionService.create(
            model=underscore(model.__class__.__name__),
            model_id=model.id,
            action=action,
            parameters=parameters,
        )
