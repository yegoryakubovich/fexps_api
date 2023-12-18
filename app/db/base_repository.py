from typing import TypeVar, Generic, Type, List, Optional

from sqlalchemy import select, delete

from app.db.base_class import Base
from app.db.session import SessionLocal

ModelType = TypeVar('ModelType', bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    @staticmethod
    def get_session():
        return SessionLocal()

    async def is_exists(self, **filters) -> bool:
        async with self.get_session() as session:
            result = await session.execute(select(self.model).filter_by(**filters))
            if not result.scalars().all():
                return False
            return True

    async def get(self, id: int) -> Optional[ModelType]:
        async with self.get_session() as session:
            result = await session.execute(select(self.model).where(self.model.id == id))
            return result.scalars().first()

    async def create(self, **obj_in_data) -> ModelType:
        async with self.get_session() as session:
            db_obj = self.model(**obj_in_data)

            session.add(db_obj)

            await session.commit()
            await session.refresh(db_obj)

            return db_obj

    async def get_all(self, **filters) -> List[ModelType]:
        async with self.get_session() as session:
            result = await session.execute(select(self.model).filter_by(**filters))
            return result.scalars().all()

    async def get_list(self) -> List[ModelType]:
        result = await self.get_all(is_deleted=False)
        return result

    async def remove(self, id: int):
        async with self.get_session() as session:
            await session.execute(delete(self.model).where(self.model.id == id))
            await session.commit()

    async def update(self, db_obj: ModelType, **obj_in_data) -> ModelType:
        async with self.get_session() as session:
            for field, value in obj_in_data.items():
                setattr(db_obj, field, obj_in_data[field])
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
