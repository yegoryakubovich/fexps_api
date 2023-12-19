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


from json import dumps
from select import select
from typing import Optional

import app.repositories as repo
from .base import BaseRepository, ModelDoesNotExist
from app.db.models import TextPack, Language
from config import PATH_TEXTS_PACKS


class TextPackRepository(BaseRepository[TextPack]):

    async def create_by_language(self, language: Language) -> Optional[TextPack]:
        json = {}
        for text in await repo.text.get_all():
            value = await repo.text.get_value(text, language=language)
            key = text.key
            json[key] = value
        text_pack = await self.create(language=language)
        with open(f'{PATH_TEXTS_PACKS}/{text_pack.id}.json', encoding='utf-8', mode='w') as md_file:
            md_file.write(dumps(json))
        return text_pack

    async def create_all(self):
        for language in await repo.language.get_all():
            await self.create_by_language(language=language)

    async def get_current(self, language: Language) -> Optional[TextPack]:
        async with self.get_session() as session:
            result = await session.execute(
                select(self.model).order_by(self.model.id.desc()).filter_by(language=language, is_deleted=False)
            )
            text_pack_all = result.scalars().all()
        if not text_pack_all:
            return await self.get(id_=0)
        return text_pack_all[0]



text_pack = TextPackRepository(TextPack)
