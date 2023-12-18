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
from .base import BaseRepository
from app.db.models import Text, Language


class TextRepository(BaseRepository[Text]):

    async def get_by_id(self, id: int) -> Optional[Text]:
        result = await self.get(id_=id)
        if not result:
            return
        if result.is_deleted:
            return
        return result

    async def delete(self, db_obj: Text) -> Optional[Text]:
        return await self.update(db_obj, is_deleted=True)

    async def get_by_key(self, key: str) -> Optional[Text]:
        async with self.get_session() as session:
            result = await session.execute(select(self.model).where(self.model.key == key))
            return result.scalars().first()

    async def get_value(self, db_obj: Text, language: Language = None) -> str:
        if language:
            result = await repo.text_translation.get_all(text=db_obj, language=language, is_deleted=False)
            if result:
                return result[0].value
        return db_obj.value_default


text = TextRepository(Text)
