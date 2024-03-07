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

from sqlalchemy import Column, Boolean, ForeignKey, BigInteger, String, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class TransferTypes:
    IN_ORDER = 'in_order'
    PAYMENT = 'payment'

    choices = [IN_ORDER, PAYMENT]


class TransferOperations:
    SEND = 'send'
    RECEIVE = 'receive'


class Transfer(Base):
    __tablename__ = 'transfers'

    id = Column(BigInteger, primary_key=True)

    type = Column(String(length=16))
    wallet_from_id = Column(BigInteger, ForeignKey('wallets.id', ondelete='SET NULL'), nullable=True)
    wallet_from = relationship('Wallet', foreign_keys=wallet_from_id, uselist=False, lazy='selectin')
    wallet_to_id = Column(BigInteger, ForeignKey('wallets.id', ondelete='SET NULL'), nullable=True)
    wallet_to = relationship('Wallet', foreign_keys=wallet_to_id, uselist=False, lazy='selectin')
    order_id = Column(BigInteger, ForeignKey('orders.id', ondelete='SET NULL'), nullable=True)
    order = relationship('Order', foreign_keys=order_id, uselist=False, lazy='selectin')
    value = Column(BigInteger, default=0)
    date = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
