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


from sqlalchemy import Column, BigInteger, Boolean, ForeignKey, Float, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class RequisiteTypes:
    INPUT = 'input'
    OUTPUT = 'output'

    choices = [INPUT, OUTPUT]


class Requisite(Base):
    __tablename__ = 'requisites'

    id = Column(BigInteger, primary_key=True)
    type = Column(String(length=8))
    wallet_id = Column(BigInteger, ForeignKey('wallets.id', ondelete='SET NULL'), nullable=True)
    wallet = relationship('Wallet', uselist=False, lazy='selectin')
    requisite_data_id = Column(BigInteger, ForeignKey('requisites_datas.id', ondelete='SET NULL'), nullable=True)
    requisite_data = relationship('RequisiteData', uselist=False, lazy='selectin')
    currency_id = Column(BigInteger, ForeignKey('currencies.id', ondelete='SET NULL'), nullable=True)
    currency = relationship('Currency', uselist=False, lazy='selectin')
    currency_value = Column(Float(), default=0)
    rate = Column(Float())
    value = Column(Float())
    total_value = Column(Float())
    value_min = Column(Float(), default=1)
    value_max = Column(Float(), default=100)
    is_deleted = Column(Boolean, default=False)
