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


import app.repositories as repo
from app.db.models import Session, Text
from app.services.base import BaseService
from app.utils.decorators import session_required


class TextService(BaseService):
    @session_required(return_model=False)
    async def get_list(
            self,
    ) -> dict:
        texts_list = []

        texts = await repo.text.get_list()
        for text in texts:
            text: Text
            translations = await repo.text_translation.get_list_by_text(text=text)
            texts_list.append(
                {
                    'key': text.key,
                    'value_default': text.value_default,
                    'translations': [
                        {
                            'language': (await repo.text_translation.get(translation.id)).id_str,
                            'value': translation.value,
                        }
                        for translation in translations
                    ],
                }
            )
        return {
            'texts': texts_list,
        }

    @session_required()
    async def create(
            self,
            session: Session,
            key: str,
            value_default: str,
            return_model: bool = False,
    ) -> dict | Text:
        text = await repo.text.create_text(
            key=key,
            value_default=value_default,
        )
        await self.create_action(
            model=text,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'key': key,
                'value_default': value_default,
            },
        )
        if return_model:
            return text
        return {'id': text.id}

    @session_required()
    async def update(
            self,
            session: Session,
            key: str,
            value_default: str = None,
            new_key: str = None,
    ) -> dict:
        text = await repo.text.get_by_key(key=key)
        await repo.text.update_text(
            text,
            value_default=value_default,
            new_key=new_key,
        )

        action_parameters = {
            'updater': f'session_{session.id}',
            'key': key,

        }
        if value_default:
            action_parameters.update(
                {
                    'value_default': value_default,
                }
            )
        if new_key:
            action_parameters.update(
                {
                    'new_key': new_key,
                }
            )

        await self.create_action(
            model=text,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            key: str,
    ) -> dict:
        text = await repo.text.get_by_key(key=key)
        await repo.text.delete(text)
        await self.create_action(
            model=text,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'key': key,
            },
        )

        return {}
