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


from sqlalchemy import Column, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class NotificationMethod(Base):
    __tablename__ = 'notifications_methods'

    id = Column(BigInteger, primary_key=True)
    method_id = Column(BigInteger, ForeignKey('methods.id', ondelete='SET NULL'))
    method = relationship('Method', foreign_keys=method_id, uselist=False, lazy='selectin')
    language_id = Column(BigInteger, ForeignKey('languages.id', ondelete='SET NULL'), nullable=True)
    language = relationship('Language', foreign_keys=language_id, uselist=False, lazy='selectin')
    telegram_id = Column(BigInteger)
    is_active = Column(Boolean, default=False)
    is_system = Column(Boolean, default=True)
    is_requisite = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
