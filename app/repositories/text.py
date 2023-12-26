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


from app.db.models import Text, Language
from .base import BaseRepository
from .text_translation import TextTranslationRepository
from ..utils import ApiException


class TextDoesNotExist(ApiException):
    pass


class TextExist(ApiException):
    pass


class NoRequiredParameters(ApiException):
    pass


class TextRepository(BaseRepository[Text]):
    model = Text

    async def get_by_key(self, key: str) -> Text:
        result = await self.get(key=key)
        if not result:
            raise TextDoesNotExist(f'Text with key "{key}" does not exist')
        return result

    @staticmethod
    async def get_value(db_obj: Text, language: Language = None) -> str:
        if language:
            result = await TextTranslationRepository().get(text=db_obj, language=language)
            if result:
                return result.value
        return db_obj.value_default

    async def create(self, key: str, value_default: str) -> Text:
        if await self.get(key=key):
            raise TextExist(f'Text with key "{key}" already exist')
        return await super().create(key=key, value_default=value_default)

    async def update_text(self, db_obj: Text, value_default: str = None, new_key: str = None):
        if value_default:
            await self.update(db_obj, value_default=value_default)
        if new_key:
            await self.update(db_obj, key=new_key)
        if not value_default and not new_key:
            raise NoRequiredParameters('One of the following parameters must be filled in: value_default, new_key')
