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
from typing import Optional

from app.db.models import TextPack, Language
from config import settings
from .base import BaseRepository
from .language import LanguageRepository
from .text import TextRepository
from app.utils.exaptions.text import TextPackDoesNotExist


class TextPackRepository(BaseRepository[TextPack]):
    model = TextPack

    async def create_by_language(self, language: Language) -> Optional[TextPack]:
        json = {}
        for text in await TextRepository().get_list():
            value = await TextRepository().get_value(text, language=language)
            key = text.key
            json[key] = value
        text_pack = await self.create(language=language)
        with open(f'{settings.path_texts_packs}/{text_pack.id}.json', encoding='utf-8', mode='w') as md_file:
            md_file.write(dumps(json, ensure_ascii=False))
        return text_pack

    async def create_all(self):
        for language in await LanguageRepository().get_list():
            await self.create_by_language(language=language)

    async def get_current(self, language: Language) -> Optional[TextPack]:
        text_pack_all = await self.get_list(language=language)
        if not text_pack_all:
            raise TextPackDoesNotExist(f'TextPack with language "{language.name}" does not exist')
        return text_pack_all[0]
