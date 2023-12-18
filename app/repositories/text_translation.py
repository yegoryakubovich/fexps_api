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
from typing import Optional, List

from app.db.base_repository import BaseRepository
from app.db.models import TextTranslation, Text, Language


class TextTranslationRepository(BaseRepository[TextTranslation]):

    async def get_by_id(self, id: int) -> Optional[TextTranslation]:
        result = await self.get(id=id)
        if not result:
            return
        if result.is_deleted:
            return
        return result

    async def delete(self, db_obj: TextTranslation) -> Optional[TextTranslation]:
        return await self.update(db_obj, is_deleted=True)

    async def get_by_text_lang(self, text: Text, language: Language) -> Optional[TextTranslation]:
        result = await self.get_all(text=text, language=language, is_deleted=False)
        if result:
            return result[0]

    async def get_list_by_text(self, text: Text) -> List[TextTranslation]:
        return await self.get_all(text=text, is_deleted=False)

    async def create(self, text: Text, language: Language, value:str):
        result = await self.get_all(text=text, language=language)
        if result:
            return result
        return await self.create(text=text, language=language,value=value)





text_translation = TextTranslationRepository(TextTranslation)
