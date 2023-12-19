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


from typing import Optional

from sqlalchemy import select

import app.repositories as repo
from app.db.models import Text, Language
from .base import BaseRepository, ModelDoesNotExist
from ..utils import ApiException


class TextDoesNotExist(ApiException):
    pass


class TextExist(ApiException):
    pass


class NoRequiredParameters(ApiException):
    pass


class TextRepository(BaseRepository[Text]):

    async def get_by_id(self, id_: int) -> Optional[Text]:
        result = await self.get(id_=id_)
        if not result or result.is_deleted:
            raise ModelDoesNotExist(f'{self.model.__name__}.{id_} does not exist')
        return result

    async def delete(self, db_obj: Text) -> Optional[Text]:
        return await self.update(db_obj, is_deleted=True)

    async def get_by_key(self, key: str) -> Optional[Text]:
        result = await self.get_all(key=key, is_deleted=False)
        if not result:
            raise TextDoesNotExist(f'Text with key "{key}" does not exist')
        return result[0]

    async def get_value(self, db_obj: Text, language: Language = None) -> str:
        if language:
            result = await repo.text_translation.get_all(text=db_obj, language=language, is_deleted=False)
            if result:
                return result[0].value
        return db_obj.value_default

    async def create_text(self, key: str, value_default: str):
        if await self.get_all(key=key):
            raise TextExist(f'Text with key "{key}" already exist')
        return await self.create(key=key, value_default=value_default)

    async def update_text(self, db_obj: Text, value_default: str = None, new_key: str = None):
        if value_default:
            await self.update(db_obj, value_default=value_default)
        if new_key:
            await self.update(db_obj, key=new_key)
        if not value_default and not new_key:
            raise NoRequiredParameters('One of the following parameters must be filled in: value_default, new_key')


text = TextRepository(Text)
