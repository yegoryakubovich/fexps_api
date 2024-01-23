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


from decimal import Decimal
from math import ceil
from types import NoneType
from typing import TypeVar, Generic, List, Optional, Any

from sqlalchemy import select

from app.db.base_class import Base
from app.db.models import Action, ActionParameter
from app.db.session import SessionLocal
from app.utils.exaptions.main import ModelDoesNotExist
from config import ITEMS_PER_PAGE

ModelType = TypeVar('ModelType', bound=Base)


class BaseRepository(Generic[ModelType]):
    model: Any

    async def is_exist(self, **filters) -> bool:
        result = await self.get(**filters)
        if result:
            return True
        return False

    async def create(self, **obj_in_data) -> ModelType:
        obj_in_data = self._convert_obj(obj_in_data)
        async with self._get_session() as session:
            db_obj = self.model(**obj_in_data)

            session.add(db_obj)

            await session.commit()
            await session.refresh(db_obj)

            return db_obj

    async def get_list(self, custom_where=None, **filters) -> List[ModelType]:
        if self.model.__name__ not in [Action.__name__, ActionParameter.__name__]:
            filters['is_deleted'] = False
        custom_select = select(self.model)
        if custom_where is not None:
            custom_select = custom_select.where(custom_where)
        async with self._get_session() as session:
            result = await session.execute(custom_select.order_by(self.model.id.desc()).filter_by(**filters))
            return result.scalars().all()

    async def get_by_id(self, id_: int) -> Optional[ModelType]:
        result = await self.get(id=id_)
        if not result:
            raise ModelDoesNotExist(f'{self.model.__name__}.{id_} does not exist')
        return result

    async def get_by_id_str(self, id_str: str) -> Optional[ModelType]:
        result = await self.get(id_str=id_str)
        if not result:
            raise ModelDoesNotExist(f'{self.model.__name__} "{id_str}" does not exist')
        return result

    async def get(self, custom_where=None, **filters) -> Optional[ModelType]:
        if self.model.__name__ not in [Action.__name__, ActionParameter.__name__]:
            filters['is_deleted'] = False
        custom_select = select(self.model)
        if custom_where is not None:
            custom_select = custom_select.where(custom_where)
        async with self._get_session() as session:
            result = await session.execute(custom_select.order_by(self.model.id.desc()).filter_by(**filters))
            return result.scalars().first()

    async def update(self, db_obj: ModelType, **obj_in_data) -> ModelType:
        obj_in_data = self._convert_obj(obj_in_data)
        async with self._get_session() as session:
            for field, value in obj_in_data.items():
                setattr(db_obj, field, obj_in_data[field])
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def delete(self, db_obj: ModelType) -> Optional[ModelType]:
        return await self.update(db_obj, is_deleted=True)

    @staticmethod
    def _get_session():
        return SessionLocal()

    @staticmethod
    def _convert_obj(obj_in_data: dict) -> dict:
        result = {}
        for key, value in obj_in_data.items():
            if type(value) in [str, int, float, bool, list, dict, NoneType, Decimal]:
                result[key] = value
                continue
            result[f"{key}_id"] = value.id
        return result

    async def count(self, custom_select, **filters):
        async with self._get_session() as session:
            if self.model.__name__ not in [Action.__name__, ActionParameter.__name__]:
                filters['is_deleted'] = False
            result = await session.execute(custom_select.filter_by(**filters))
            return len(result.scalars().all())

    async def search(self, page: int, custom_where=None, **filters) -> tuple[List[ModelType], int, int]:
        if custom_where is None:
            custom_select = select(self.model)
        else:
            custom_select = select(self.model).where(custom_where)

        async with self._get_session() as session:
            if self.model.__name__ not in [Action.__name__, ActionParameter.__name__]:
                filters['is_deleted'] = False
            result = await session.execute(
                custom_select.filter_by(**filters).order_by(
                    self.model.id.desc()
                ).limit(ITEMS_PER_PAGE).offset(ITEMS_PER_PAGE * (page - 1))
            )
            count = await self.count(custom_select, **filters)
            return result.scalars().all(), count, ceil(count / ITEMS_PER_PAGE)
