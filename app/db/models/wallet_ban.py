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


from sqlalchemy import Column, BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class WalletBanReasons:
    BY_ADMIN = 'by_admin'
    BY_ORDER = 'by_order'

    choices = [BY_ADMIN, BY_ORDER]


class WalletBan(Base):
    __tablename__ = 'wallets_bans'

    id = Column(BigInteger, primary_key=True)

    wallet_id = Column(BigInteger, ForeignKey('wallets.id', ondelete='SET NULL'))
    wallet = relationship('Wallet', foreign_keys=wallet_id, uselist=False, lazy='selectin')
    value = Column(BigInteger, default=0)
    reason = Column(String(length=16))
    is_deleted = Column(Boolean, default=False)
