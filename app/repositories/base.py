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


from typing import TypeVar, Generic, List, Optional, Any

from sqlalchemy import select

from app.db.base_class import Base
from app.db.session import SessionLocal
from app.utils import ApiException

ModelType = TypeVar('ModelType', bound=Base)


class ModelDoesNotExist(ApiException):
    pass


class BaseRepository(Generic[ModelType]):
    model: Any

    @staticmethod
    def get_session():
        return SessionLocal()

    @staticmethod
    def convert_obj(obj_in_data: dict) -> dict:
        result = {}
        for key, value in obj_in_data.items():
            if not value:
                continue
            print(f"{type(value)} - {value}")
            if isinstance(value, str) or isinstance(value, int) or isinstance(value, bool):
                result[key] = value
                continue
            result[f"{key}_id"] = value.id
        return result

    async def is_exist(self, **filters) -> bool:
        result = await self.get(**filters)
        if result:
            return True
        return False

    async def get(self, **filters) -> Optional[ModelType]:
        async with self.get_session() as session:
            result = await session.execute(
                select(self.model).order_by(self.model.id.desc()).filter_by(is_deleted=False, **filters)
            )
            return result.scalars().first()

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

    async def create(self, **obj_in_data) -> ModelType:
        obj_in_data = self.convert_obj(obj_in_data)
        async with self.get_session() as session:
            db_obj = self.model(**obj_in_data)

            session.add(db_obj)

            await session.commit()
            await session.refresh(db_obj)

            return db_obj

    async def get_list(self, **filters) -> List[ModelType]:
        async with self.get_session() as session:
            result = await session.execute(
                select(self.model).order_by(self.model.id.desc()).filter_by(is_deleted=False, **filters)
            )
            return result.scalars().all()

    async def delete(self, db_obj: ModelType) -> Optional[ModelType]:
        return await self.update(db_obj, is_deleted=True)

    async def update(self, db_obj: ModelType, **obj_in_data) -> ModelType:
        obj_in_data = self.convert_obj(obj_in_data)
        async with self.get_session() as session:
            for field, value in obj_in_data.items():
                setattr(db_obj, field, obj_in_data[field])

            session.add(db_obj)

            await session.commit()
            await session.refresh(db_obj)

            return db_obj
