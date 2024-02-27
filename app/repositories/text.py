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


from peewee import DoesNotExist

from app.db.models import Text, Language, TextTranslation
from app.repositories.base import BaseRepository
from app.utils.exceptions import ModelDoesNotExist


class TextRepository(BaseRepository):
    model = Text

    @staticmethod
    async def get_by_key(key: str) -> Text:
        try:
            return Text.get(
                (Text.key == key) &
                (Text.is_deleted == False)
            )
        except DoesNotExist:
            raise ModelDoesNotExist(
                kwargs={
                    'model': 'Text',
                    'id_type': 'key',
                    'id_value': key,
                },
            )

    @staticmethod
    async def get_value(text: Text, language: Language = None) -> str:
        try:
            translation = TextTranslation.get(
                (TextTranslation.text == text) &
                (TextTranslation.language == language) &
                (TextTranslation.is_deleted == False)
            )
            value = translation.value
        except DoesNotExist:
            value = text.value_default
        return value
