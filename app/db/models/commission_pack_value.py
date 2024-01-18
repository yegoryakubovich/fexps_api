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


from sqlalchemy import Column, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CommissionPackValue(Base):
    __tablename__ = 'commissions_packs_values'

    id = Column(BigInteger, primary_key=True)
    commission_pack_id = Column(BigInteger, ForeignKey('wallets.id', ondelete='SET NULL'), nullable=True, unique=True)
    commission_pack = relationship('Wallet', foreign_keys=commission_pack_id, uselist=False, lazy='selectin')
    value_from = Column(BigInteger)
    value_to = Column(BigInteger)
    value = Column(BigInteger, nullable=True)
    percent = Column(BigInteger, nullable=True)

    is_deleted = Column(Boolean, default=False)
