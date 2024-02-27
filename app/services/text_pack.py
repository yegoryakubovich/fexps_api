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


from json import loads

from app.db.models import TextPack, Session
from app.repositories import TextPackRepository, LanguageRepository
from app.services.base import BaseService
from app.utils.decorators import session_required
from config import settings


class TextPackService(BaseService):
    model = TextPack

    @staticmethod
    async def get(language_id_str: str):
        language = await LanguageRepository().get_by_id_str(id_str=language_id_str)
        text_pack = await TextPackRepository.get_current(language=language)

        if text_pack.id == 0:
            return {
                'text_pack_id': text_pack.id,
                'text_pack': {},
            }

        with open(f'{settings.path_texts_packs}/{text_pack.id}.json', encoding='utf-8', mode='r') as md_file:
            json_str = md_file.read()

        json = loads(json_str)
        return {
            'text_pack_id': text_pack.id,
            'text_pack': json,
        }

    @session_required(permissions=['texts'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            language_id_str: str,
    ):
        language = await LanguageRepository().get_by_id_str(id_str=language_id_str)
        text_pack = await TextPackRepository.create(language=language)
        await self.create_action(
            model=text_pack,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'by_admin': True,
            },
        )
        return {
            'id': text_pack.id,
        }

    @session_required(permissions=['texts'], can_root=True)
    async def create_all_by_admin(
            self,
            session: Session,
    ):
        languages = await LanguageRepository().get_list()
        for language in languages:
            await self.create_by_admin(session=session, language_id_str=language.id_str)

    @session_required(permissions=['texts'])
    async def delete_by_admin(self, session: Session, id_: int):
        text_pack = await TextPackRepository().get_by_id(id_=id_)
        await TextPackRepository().delete(model=text_pack)
        await self.create_action(
            model=text_pack,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            },
        )
        return {}
