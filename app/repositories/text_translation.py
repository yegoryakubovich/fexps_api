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


from typing import Optional, List

from app.db.models import TextTranslation, Text, Language
from .base import BaseRepository
from ..utils import ApiException


class TextTranslationDoesNotExist(ApiException):
    pass


class TextTranslationExist(ApiException):
    pass


class TextTranslationRepository(BaseRepository[TextTranslation]):
    model = TextTranslation

    async def get_by_text_lang(self, text: Text, language: Language) -> Optional[TextTranslation]:
        result = await self.get_list(text=text, language=language)
        if not result:
            raise TextTranslationDoesNotExist(f'Text translation with language "{language.id_str}" does not exist')
        return result[0]

    async def get_list_by_text(self, text: Text) -> List[TextTranslation]:
        return await self.get_list(text=text)
