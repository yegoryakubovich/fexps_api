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


from app.db.models import Language, Session, Text, TextTranslation, Actions
from app.repositories import LanguageRepository, TextRepository, TextTranslationRepository
from app.services.base import BaseService
from app.services.text_pack import TextPackService
from app.utils.decorators import session_required
from app.utils.exceptions import ModelAlreadyExist


class TextTranslationService(BaseService):
    @session_required(permissions=['texts'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            text_key: str,
            language: str,
            value: str,
            return_model: bool = False,
            create_text_pack: bool = True,
    ) -> dict | TextTranslation:
        text: Text = await TextRepository().get_by_key(key=text_key)
        language: Language = await LanguageRepository().get_by_id_str(id_str=language)
        if await TextTranslationRepository().get(text=text, language=language):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'TextTranslation',
                    'id_type': 'language',
                    'id_value': language.id_str,
                },
            )
        text_translation = await TextTranslationRepository().create(
            text=text,
            language=language,
            value=value,
        )
        await self.create_action(
            model=text_translation,
            action=Actions.CREATE,
            parameters={
                'creator': f'session_{session.id}',
                'text_key': text_key,
                'language': language.id_str,
                'value': value,
                'by_admin': True,
            },
        )
        if create_text_pack:
            await TextPackService().create_all_by_admin(session=session)
        if return_model:
            return text_translation
        return {
            'id': text_translation.id,
        }

    @session_required(permissions=['texts'], can_root=True)
    async def update_by_admin(
            self,
            session: Session,
            text_key: str,
            language: str,
            value: str,
            create_text_pack: bool = True,
    ) -> dict:
        text: Text = await TextRepository().get_by_key(key=text_key)
        language: Language = await LanguageRepository().get_by_id_str(id_str=language)
        text_translation: TextTranslation = await TextTranslationRepository().get(text=text, language=language)

        await TextTranslationRepository().update(
            model=text_translation,
            value=value,
        )
        await self.create_action(
            model=text_translation,
            action=Actions.UPDATE,
            parameters={
                'updater': f'session_{session.id}',
                'text_key': text_key,
                'language': language.id_str,
                'value': value,
                'by_admin': True,
            },
        )
        if create_text_pack:
            await TextPackService().create_all_by_admin(session=session)
        return {}

    @session_required(permissions=['texts'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            text_key: str,
            language: str,
            create_text_pack: bool = True,
    ) -> dict:
        text: Text = await TextRepository().get_by_key(key=text_key)
        language: Language = await LanguageRepository().get_by_id_str(id_str=language)
        text_translation: TextTranslation = await TextTranslationRepository().get(text=text, language=language)
        await TextTranslationRepository().delete(
            model=text_translation,
        )
        await self.create_action(
            model=text_translation,
            action=Actions.DELETE,
            parameters={
                'deleter': f'session_{session.id}',
                'text_key': text_key,
                'language': language.id_str,
                'by_admin': True,
            },
        )
        if create_text_pack:
            await TextPackService().create_all_by_admin(session=session)
        return {}
