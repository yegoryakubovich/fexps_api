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


import logging
from typing import List, Optional

from inflection import underscore

from app.db.base_class import Base
from app.db.models import Action, Actions
from app.repositories import ActionParameterRepository, ActionRepository


class ActionService:
    model = Action

    @staticmethod
    async def create(
            model: str,
            model_id: int,
            action: str,
            parameters: dict = None,
    ) -> None:
        if not parameters:
            parameters = {}
        action = await ActionRepository().create(model=model, model_id=model_id, action=action)
        params_str = ''
        for key, value in parameters.items():
            await ActionRepository().create_parameter(action=action, key=key, value=str(value))
            if not value:
                value = 'none'
            params_str += f'{key.upper()} = {str(value).upper()}\n'
        logging.debug(
            msg=f'ACTION: {action.model.upper()}.{action.model_id}.{action.action.upper()}. '
                f'PARAMS: \n{params_str}',
        )

    @staticmethod
    async def get_action(
            model: Base,
            action: Actions,
            **parameters,
    ) -> Optional[Action]:
        """
        :param model: Model object
        :param action: action
        :param parameters: Only one parameter
        :return: Action if found else None
        """
        parameter = None
        for key, value in parameters.items():
            parameter = key, value
            break
        for action_db in await ActionService().get_actions(model, action=action):
            action_param = await ActionParameterRepository().get(action=action_db)
            if parameter:
                action_param = await ActionParameterRepository().get(
                    action=action_db,
                    key=parameter[0],
                    value=parameter[1],
                )
            if not action_param:
                continue
            return action_db

    @staticmethod
    async def get_actions(
            model: Base,
            action: Actions,
    ) -> List[Action]:
        actions_db = await ActionRepository().get_list(
            model=underscore(model.__class__.__name__),
            model_id=model.id,
            action=action
        )
        return actions_db
