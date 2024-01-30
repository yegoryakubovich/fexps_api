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


from app.db.models import Session, Text, Actions
from app.repositories.text import TextExist, TextRepository
from app.repositories.text_translation import TextTranslationRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class TextService(BaseService):
    model = Text

    @session_required(permissions=['texts'])
    async def create(
            self,
            session: Session,
            key: str,
            value_default: str,
            return_model: bool = False,
    ) -> dict | Text:
        if await TextRepository().get(key=key):
            raise TextExist(f'Text with key "{key}" already exist')
        text = await TextRepository().create(key=key, value_default=value_default)
        await self.create_action(
            model=text,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'key': key,
                'value_default': value_default,
            },
        )
        if return_model:
            return text
        return {'id': text.id}

    @session_required(return_model=False, permissions=['texts'])
    async def get_list(
            self,
    ) -> dict:
        texts_list = []
        texts = await TextRepository().get_list()
        for text in texts:
            text: Text
            translations = await TextTranslationRepository().get_list_by_text(text=text)
            texts_list.append(
                {
                    'key': text.key,
                    'value_default': text.value_default,
                    'translations': [
                        {
                            'language': translation.language.id_str,
                            'value': translation.value,
                        }
                        for translation in translations
                    ],
                }
            )

        return {'texts': texts_list}

    @session_required(permissions=['texts'])
    async def update(
            self,
            session: Session,
            key: str,
            value_default: str = None,
            new_key: str = None,
    ) -> dict:
        text = await TextRepository().get_by_key(key=key)
        await TextRepository().update_text(
            text,
            value_default=value_default,
            new_key=new_key,
        )
        action_parameters = {
            'updater': f'session_{session.id}',
            'key': key,
        }
        if value_default:
            action_parameters['value_default'] = value_default
        if new_key:
            action_parameters['new_key'] = new_key

        await self.create_action(
            model=text,
            action=Actions.UPDATE,
            parameters=action_parameters,
        )
        return {}

    @session_required(permissions=['texts'])
    async def delete(
            self,
            session: Session,
            key: str,
    ) -> dict:
        text = await TextRepository().get_by_key(key=key)
        await TextRepository().delete(text)
        await self.create_action(
            model=text,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'key': key,
            },
        )
        return {}
