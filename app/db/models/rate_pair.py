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
    commission_pack_value_id = Column(
        BigInteger,
        ForeignKey('commissions_packs_values.id', ondelete='SET NULL'),
        nullable=True,
    )
    commission_pack_value = relationship(
        'CommissionPackValue',
        foreign_keys=commission_pack_value_id,
        uselist=False,
        lazy='selectin',
    )
    input_method_id = Column(BigInteger, ForeignKey('methods.id', ondelete='SET NULL'))
    input_method = relationship(argument='Method', foreign_keys=input_method_id, uselist=False, lazy='selectin')
    output_method_id = Column(BigInteger, ForeignKey('methods.id', ondelete='SET NULL'))
    output_method = relationship(argument='Method', foreign_keys=output_method_id, uselist=False, lazy='selectin')
    rate_decimal = Column(Integer, default=2)
    rate = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.now)
    is_deleted = Column(Boolean, default=False)
