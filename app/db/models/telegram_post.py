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


from sqlalchemy import Column, BigInteger, Boolean, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class TelegramPost(Base):
    __tablename__ = 'telegrams_posts'

    id = Column(BigInteger, primary_key=True)
    commission_pack_id = Column(BigInteger, ForeignKey('commissions_packs.id', ondelete='SET NULL'), nullable=True)
    commission_pack = relationship('CommissionPack', foreign_keys=commission_pack_id, uselist=False, lazy='selectin')
    data = Column(JSON())
    is_deleted = Column(Boolean, default=False)
