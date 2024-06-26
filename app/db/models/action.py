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


from datetime import datetime
from enum import Enum

from sqlalchemy import Column, BigInteger, String, DateTime

from app.db.base_class import Base


class Actions:
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'


class Action(Base):
    __tablename__ = 'actions'

    id = Column(BigInteger, primary_key=True)
    datetime = Column(DateTime, default=datetime.now)
    model = Column(String(length=64))
    model_id = Column(BigInteger)
    action = Column(String(length=256))
