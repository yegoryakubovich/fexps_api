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


import datetime

from sqlalchemy import Column, BigInteger, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class RateParse(Base):
    __tablename__ = 'rates_parsers'

    id = Column(BigInteger, primary_key=True)
    currency_id = Column(BigInteger, ForeignKey('currencies.id', ondelete='SET NULL'))
    currency = relationship(argument='Currency', foreign_keys=currency_id, uselist=False, lazy='selectin')
    type = Column(String(length=16))
    source = Column(String(length=32))
    rate = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.now)
    is_deleted = Column(Boolean, default=False)
