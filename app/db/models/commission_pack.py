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


class CommissionPackTelegramTypes:
    FEXPS = 'fexps'
    SOWAPAY = 'sowapay'


class CommissionPack(Base):
    __tablename__ = 'commissions_packs'

    id = Column(BigInteger, primary_key=True)
    name_text_id = Column(BigInteger, ForeignKey('texts.id'))
    name_text = relationship('Text', foreign_keys=name_text_id, uselist=False, lazy='selectin')
    telegram_chat_id = Column(BigInteger, nullable=True)
    telegram_type = Column(String(length=32), nullable=True)
    is_default = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
