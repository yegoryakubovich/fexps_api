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


from typing import TypeVar, Generic, Type, List, Optional

from sqlalchemy import select, delete

from app.db.base_class import Base
from app.db.session import SessionLocal
from app.utils import ApiException

ModelType = TypeVar('ModelType', bound=Base)


class ModelDoesNotExist(ApiException):
    pass


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    @staticmethod
    def get_session():
        return SessionLocal()

    async def is_exist(self, **filters) -> bool:
        result = await self.get_all(**filters)
        if result:
            return True
        return False

    async def delete(self, db_obj: ModelType) -> Optional[ModelType]:
        return await self.update(db_obj, is_deleted=True)

    async def get(self, id_: int) -> Optional[ModelType]:
        async with self.get_session() as session:
            result = await session.execute(select(self.model).where(self.model.id == id_))
            return result.scalars().first()

    async def get_by_id(self, id_: int) -> Optional[ModelType]:
        result = await self.get_all(id_=id_, is_deleted=False)
        if not result:
            raise ModelDoesNotExist(f'{self.model.__name__}.{id_} does not exist')
        return result[0]

    async def get_by_id_str(self, id_str: str) -> Optional[ModelType]:
        result = await self.get_all(id_str=id_str, is_deleted=False)
        if not result:
            raise ModelDoesNotExist(f'{self.model.__name__} "{id_str}" does not exist')
        return result[0]

    async def create(self, **obj_in_data) -> ModelType:
        async with self.get_session() as session:
            db_obj = self.model(**obj_in_data)

            session.add(db_obj)

            await session.commit()
            await session.refresh(db_obj)

            return db_obj

    async def get_by(self, **filters) -> List[ModelType]:
        async with self.get_session() as session:
            result = await session.execute(select(self.model).order_by(self.model.id.desc()).filter_by(**filters))
            return result.scalars().first()

    async def get_all(self, **filters) -> List[ModelType]:
        async with self.get_session() as session:
            result = await session.execute(select(self.model).filter_by(**filters))
            return result.scalars().all()

    async def get_list(self) -> List[ModelType]:
        result = await self.get_all(is_deleted=False)
        return result

    async def remove(self, id_: int):
        async with self.get_session() as session:
            await session.execute(delete(self.model).where(self.model.id == id_))
            await session.commit()

    async def update(self, db_obj: ModelType, **obj_in_data) -> ModelType:
        async with self.get_session() as session:
            for field, value in obj_in_data.items():
                setattr(db_obj, field, obj_in_data[field])
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
