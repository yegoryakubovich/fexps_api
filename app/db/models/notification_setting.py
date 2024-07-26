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


from sqlalchemy import Column, BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class NotificationSetting(Base):
    __tablename__ = 'notifications_settings'

    id = Column(BigInteger, primary_key=True)
    account_id = Column(BigInteger, ForeignKey('accounts.id', ondelete='SET NULL'))
    account = relationship('Account', foreign_keys=account_id, uselist=False, lazy='selectin')
    telegram_id = Column(BigInteger, nullable=True)
    code = Column(String(length=128))
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=True)
    is_system_email = Column(Boolean, default=True)
    is_system_telegram = Column(Boolean, default=True)
    is_system_push = Column(Boolean, default=True)
    is_request = Column(Boolean, default=True)
    is_request_email = Column(Boolean, default=True)
    is_request_telegram = Column(Boolean, default=True)
    is_request_push = Column(Boolean, default=True)
    is_requisite = Column(Boolean, default=True)
    is_requisite_email = Column(Boolean, default=True)
    is_requisite_telegram = Column(Boolean, default=True)
    is_requisite_push = Column(Boolean, default=True)
    is_chat = Column(Boolean, default=True)
    is_chat_email = Column(Boolean, default=True)
    is_chat_telegram = Column(Boolean, default=True)
    is_chat_push = Column(Boolean, default=True)
    is_transfer = Column(Boolean, default=True)
    is_transfer_email = Column(Boolean, default=True)
    is_transfer_telegram = Column(Boolean, default=True)
    is_transfer_push = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
