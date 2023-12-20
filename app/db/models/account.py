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


from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(BigInteger, primary_key=True)

    username = Column(String(32))
    password_salt = Column(String(32))
    password_hash = Column(String(32))
    firstname = Column(String(32))
    lastname = Column(String(32))
    surname = Column(String(32), nullable=True)
    country_id = Column(BigInteger, ForeignKey("countries.id"))
    country = relationship("Country", uselist=False, lazy="selectin")
    language_id = Column(BigInteger, ForeignKey("languages.id"))
    language = relationship("Language", uselist=False, lazy="selectin")
    timezone_id = Column(BigInteger, ForeignKey("timezones.id"))
    timezone = relationship("Timezone", uselist=False, lazy="selectin")
    currency_id = Column(BigInteger, ForeignKey("currencies.id"))
    currency = relationship("Currency", uselist=False, lazy="selectin")
    is_active = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
