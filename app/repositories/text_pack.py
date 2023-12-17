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

from peewee import DoesNotExist

from app.db.models import Language, TextPack, Text
from .text import TextRepository
from .base import BaseRepository
from config import PATH_TEXTS_PACKS


class TextPackRepository(BaseRepository):
    model = TextPack

    @staticmethod
    async def create(language: Language):
        json = {}
        for text in Text.select():
            value = await TextRepository.get_value(text=text, language=language)
            key = text.key
            json[key] = value

        text_pack = TextPack.create(language=language)

        with open(f'{PATH_TEXTS_PACKS}/{text_pack.id}.json', encoding='utf-8', mode='w') as md_file:
            md_file.write(dumps(json))

        return text_pack

    async def create_all(self):
        for language in Language.select():
            await self.create(language=language)

    @staticmethod
    async def get_current(language: Language) -> TextPack:
        try:
            text_pack = TextPack.select().where(
                (TextPack.language == language) &
                (TextPack.is_deleted == False)
            ).order_by(TextPack.id.desc()).get()
            return text_pack
        except DoesNotExist:
            return TextPack(id=0)  # FIXME

    @staticmethod
    async def delete(text_pack: TextPack):
        text_pack.is_deleted = True
        text_pack.save()
