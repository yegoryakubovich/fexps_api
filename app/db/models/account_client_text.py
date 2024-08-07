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


class AccountClientText(Base):
    __tablename__ = 'accounts_clients_texts'

    id = Column(BigInteger, primary_key=True)
    account_id = Column(BigInteger, ForeignKey('accounts.id', ondelete='SET NULL'), nullable=True)
    account = relationship('Account', foreign_keys=account_id, uselist=False, lazy='selectin')
    client_text_id = Column(BigInteger, ForeignKey('clients_texts.id', ondelete='SET NULL'), nullable=True)
    client_text = relationship('ClientText', foreign_keys=client_text_id, uselist=False, lazy='selectin')
    value = Column(String(length=2048))
    is_deleted = Column(Boolean, default=False)
