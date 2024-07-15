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


from sqlalchemy import Column, BigInteger, Boolean, ForeignKey, JSON, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class RequisiteData(Base):
    __tablename__ = 'requisites_datas'

    id = Column(BigInteger, primary_key=True)
    account_id = Column(BigInteger, ForeignKey('accounts.id', ondelete='SET NULL'), nullable=True)
    account = relationship('Account', foreign_keys=account_id, uselist=False, lazy='selectin')
    name = Column(String(length=32))
    method_id = Column(BigInteger, ForeignKey('methods.id', ondelete='SET NULL'), nullable=True)
    method = relationship('Method', foreign_keys=method_id, uselist=False, lazy='selectin')
    fields = Column(JSON())
    is_disposable = Column(Boolean)
    is_deleted = Column(Boolean, default=False)
