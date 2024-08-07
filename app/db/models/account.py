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


from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(length=32))
    password_salt = Column(String(length=32))
    password_hash = Column(String(length=32))
    firstname = Column(String(length=32))
    lastname = Column(String(length=32))
    country_id = Column(BigInteger, ForeignKey('countries.id', ondelete='SET NULL'), nullable=True)
    country = relationship('Country', foreign_keys=country_id, uselist=False, lazy='selectin')
    language_id = Column(BigInteger, ForeignKey('languages.id', ondelete='SET NULL'), nullable=True)
    language = relationship('Language', foreign_keys=language_id, uselist=False, lazy='selectin')
    timezone_id = Column(BigInteger, ForeignKey('timezones.id', ondelete='SET NULL'), nullable=True)
    timezone = relationship('Timezone', foreign_keys=timezone_id, uselist=False, lazy='selectin')
    currency_id = Column(BigInteger, ForeignKey('currencies.id', ondelete='SET NULL'), nullable=True)
    currency = relationship('Currency', foreign_keys=currency_id, uselist=False, lazy='selectin')
    file_id = Column(BigInteger, ForeignKey('files.id', ondelete='SET NULL'), nullable=True)
    file = relationship('File', foreign_keys=file_id, uselist=False, lazy='selectin')
    is_active = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
