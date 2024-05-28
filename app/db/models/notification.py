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


from sqlalchemy import Column, BigInteger, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class NotificationTypes:
    REQUEST_CHANGE = 'request_change'
    REQUISITE_CHANGE = 'requisite_change'
    ORDER_CHANGE = 'order_change'
    CHAT_CHANGE = 'chat_change'


class NotificationStates:
    SENT = 'sent'
    BLOCKED = 'blocked'
    ERROR = 'error'


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(BigInteger, primary_key=True)
    account_id = Column(BigInteger, ForeignKey('accounts.id', ondelete='SET NULL'))
    account = relationship('Account', uselist=False, lazy='selectin')
    type = Column(String(length=32))
    state = Column(String(length=32))
    text = Column(Text)
    is_deleted = Column(Boolean, default=False)
