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

from sqlalchemy import Column, BigInteger, ForeignKey, Boolean, Integer, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class RatePair(Base):
    __tablename__ = 'rates_pairs'

    id = Column(BigInteger, primary_key=True)
    currency_input_id = Column(BigInteger, ForeignKey('currencies.id', ondelete='SET NULL'))
    currency_input = relationship(argument='Currency', foreign_keys=currency_input_id, uselist=False, lazy='selectin')
    currency_output_id = Column(BigInteger, ForeignKey('currencies.id', ondelete='SET NULL'))
    currency_output = relationship(argument='Currency', foreign_keys=currency_output_id, uselist=False, lazy='selectin')
    rate_decimal = Column(Integer, default=2)
    value = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.now)
    is_deleted = Column(Boolean, default=False)
