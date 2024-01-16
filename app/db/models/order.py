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


from sqlalchemy import Column, BigInteger, Boolean, ForeignKey, Double, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class OrderTypes:
    INPUT = 'input'
    OUTPUT = 'output'

    choices = [INPUT, OUTPUT]


class OrderStates:
    RESERVE = 'reserve'
    PAYMENT = 'payment'
    CONFIRMATION = 'confirmation'
    COMPLETED = 'completed'
    CANCELED = 'canceled'

    choices = [RESERVE, PAYMENT, CONFIRMATION, COMPLETED, CANCELED]


class Order(Base):
    __tablename__ = 'orders'

    id = Column(BigInteger, primary_key=True)
    type = Column(String(length=8))
    state = Column(String(length=8))

    request_id = Column(BigInteger, ForeignKey('requests.id', ondelete='SET NULL'), nullable=True)
    request = relationship('Request', foreign_keys=request_id, uselist=False, lazy='selectin')
    requisite_id = Column(BigInteger, ForeignKey('requisites.id', ondelete='SET NULL'), nullable=True)
    requisite = relationship('Requisite', foreign_keys=requisite_id, uselist=False, lazy='selectin')
    currency_value = Column(BigInteger())
    value = Column(BigInteger())
    rate = Column(Double())

    is_deleted = Column(Boolean, default=False)
