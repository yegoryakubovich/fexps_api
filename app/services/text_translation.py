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


from app.db.models import Language, Session, Text, TextTranslation
import app.repositories as repo
from app.services.base import BaseService
from app.utils.decorators import session_required


class TextTranslationService(BaseService):
    @session_required()
    async def create(
            self,
            session: Session,
            text_key: str,
            language: str,
            value: str,
            return_model: bool = False
    ) -> dict | TextTranslation:
        text: Text = await repo.text.get_by_key(key=text_key)
        language: Language = await repo.language.get_by_id_str(id_str=language)
        text_translation = await repo.text_translation.create(
            text=text,
            language=language,
            value=value,
        )
        await self.create_action(
            model=text_translation,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'text_key': text_key,
                'language': language,
                'value': value,
            },
        )
        if return_model:
            return text_translation
        return {
            'translation_id': text_translation.id,
        }

    @session_required()
    async def update(
            self,
            session: Session,
            text_key: str,
            language: str,
            value: str,
    ) -> dict:
        text: Text = await repo.text.get_by_key(key=text_key)
        language: Language = await repo.language.get_by_id_str(id_str=language)
        text_translation: TextTranslation = await repo.text_translation.get(text=text, language=language)
        await repo.text_translation.update(
            text_translation=text_translation,
            value=value,
        )
        await self.create_action(
            model=text_translation,
            action='update',
            parameters={
                'updater': f'session_{session.id}',
                'text_key': text_key,
                'language': language,
                'value': value,
            },
        )

        return {}

    @session_required()
    async def delete(
            self,
            session: Session,
            text_key: str,
            language: str,
    ) -> dict:
        text: Text = await repo.text.get_by_key(key=text_key)
        language: Language = await repo.language.get_by_id_str(id_str=language)
        text_translation: TextTranslation = await repo.text_translation.get(text=text, language=language)
        await repo.text_translation.delete(
            text_translation=text_translation,
        )
        await self.create_action(
            model=text_translation,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'text_key': text_key,
                'language': language,
            },
        )

        return {}
