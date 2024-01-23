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


from sqlalchemy import Column, BigInteger, Boolean, ForeignKey, String, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class OrderRequestTypes:
    UPDATE_VALUE = 'update_value'
    CANCEL = 'cancel'

    choices = [UPDATE_VALUE, CANCEL]


class OrderRequestStates:  # FIXME
    WAIT = 'wait'
    COMPLETED = 'competed'
    CANCELED = 'canceled'

    choices = [WAIT, COMPLETED, CANCELED]


class OrderRequest(Base):
    __tablename__ = 'orders_requests'

    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey('orders.id', ondelete='SET NULL'), nullable=True)
    order = relationship('Order', foreign_keys=order_id, uselist=False, lazy='selectin')
    type = Column(String(length=16))
    state = Column(String(length=16))
    data = Column(JSON())
    is_deleted = Column(Boolean, default=False)
