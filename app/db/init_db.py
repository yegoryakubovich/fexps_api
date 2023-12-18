from app.db import base  # noqa: F401
from app.db.base import Base
from app.db.session import engine

""""""
import app.db.models, app.repositories  # noqa


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
