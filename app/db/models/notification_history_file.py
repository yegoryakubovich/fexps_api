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


class NotificationHistoryFile(Base):
    __tablename__ = 'notifications_histories_files'

    id = Column(BigInteger, primary_key=True)
    notification_history_id = Column(
        BigInteger,
        ForeignKey('notifications_histories.id', ondelete='SET NULL'),
    )
    notification_history = relationship(
        'NotificationHistory',
        foreign_keys=notification_history_id,
        uselist=False,
        lazy='selectin',
    )
    file_id = Column(BigInteger, ForeignKey('files.id', ondelete='SET NULL'), nullable=True)
    file = relationship('File', foreign_keys=file_id, uselist=False, lazy='selectin')
    is_deleted = Column(Boolean, default=False)
