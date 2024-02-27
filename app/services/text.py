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


from app.db.models import Session, Text
from app.repositories import TextRepository, TextTranslationRepository
from app.services.text_pack import TextPackService
from app.services.base import BaseService
from app.utils.decorators import session_required


class TextService(BaseService):
    @session_required(return_model=False, permissions=['texts'])
    async def get(
            self,
            key: str,
    ):
        text = await TextRepository().get_by_key(key=key)
        translations = await TextTranslationRepository().get_list_by_text(text=text)

        return {
            'text': {
                'id': text.id,
                'key': text.key,
                'value_default': text.value_default,
                'translations': [
                    {
                        'language': translation.language.id_str,
                        'value': translation.value,
                    }
                    for translation in translations
                ],
            },
        }

    @session_required(return_model=False, permissions=['texts'], can_root=True)
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
                    'id': text.id,
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
        return {
            'texts': texts_list,
        }

    @session_required(permissions=['texts'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            key: str,
            value_default: str,
            return_model: bool = False,
            create_text_pack: bool = True,
    ) -> dict | Text:
        text = await TextRepository().create(
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
                'by_admin': True,
            },
        )
        if create_text_pack:
            await TextPackService().create_all_by_admin(session=session)
        if return_model:
            return text
        return {'key': text.key}

    @session_required(permissions=['texts'])
    async def update_by_admin(
            self,
            session: Session,
            key: str,
            value_default: str = None,
            new_key: str = None,
    ) -> dict:
        text = await TextRepository().get_by_key(key=key)
        await TextRepository().update(
            model=text,
            value_default=value_default,
            new_key=new_key,
        )

        action_parameters = {
            'updater': f'session_{session.id}',
            'key': key,
            'by_admin': True,
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
        await TextPackService().create_all_by_admin(session=session)

        return {}

    @session_required(permissions=['texts'])
    async def delete_by_admin(
            self,
            session: Session,
            key: str,
    ) -> dict:
        text = await TextRepository().get_by_key(key=key)
        await TextRepository().delete(
            model=text,
        )
        await self.create_action(
            model=text,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'key': key,
                'by_admin': True,
            },
        )
        await TextPackService().create_all_by_admin(session=session)

        return {}
