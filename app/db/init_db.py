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


from app.db import base  # noqa: F401
from app.db.base import Base
from app.db.session import engine

import app.db.models, app.repositories  # noqa


async def init_db() -> None:
    async with engine.begin() as conn:
        # noinspection PyUnresolvedReferences
        await conn.run_sync(Base.metadata.create_all)
